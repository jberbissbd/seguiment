import logging
from pathlib import Path
import shutil
from uuid import uuid4

from docx.image.exceptions import UnrecognizedImageError
from docx.image.image import Image

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.report_configuration_dao import (
    ReportConfigurationDAO,
    ReportConfigurationPersistenceError,
)
from tutopy.models.messaging import Category
from tutopy.models.reporting import TermConfiguration, TermConfigurationNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.utils import AcademicCourseDeterminator
from tutopy.services.validation_service import ValidationService


LOGGER = logging.getLogger(__name__)


class ReportConfigurationService:
    """Preferències persistents per generar els informes de seguiment."""

    def __init__(self, configuration_dao: ReportConfigurationDAO,
                 courses: AcademicCourseDAO, categories: CategoryDAO,
                 transaction_factory, storage_dir: str | Path | None = None,
                 validation_service: ValidationService = None):
        self.configuration_dao = configuration_dao
        self.courses = courses
        self.categories = categories
        self.transaction_factory = transaction_factory
        self.validation = validation_service or ValidationService()
        self.storage_dir = Path(storage_dir) if storage_dir else None

    def get_term_configurations(self) -> list[TermConfiguration]:
        return self.configuration_dao.get_term_configurations()

    def get_term_configuration(self, academic_course_id: int,
                               group_name: str) -> TermConfiguration | None:
        self.validation.positive_id(academic_course_id)
        group_name = self.validation.required_text(group_name, "El grup és obligatori.")
        return self.configuration_dao.get_term_configuration(
            academic_course_id, group_name
        )

    def save_term_configuration(self, data: TermConfigurationNew) -> TermConfiguration:
        course = self.courses.get_by_id(
            self.validation.positive_id(data.academic_course_id)
        )
        if course is None:
            raise EntityNotFoundError("El curs acadèmic seleccionat no existeix.")
        group_name = self.validation.required_text(data.group_name, "El grup és obligatori.")
        second = self.validation.iso_date(data.second_term_start)
        third = self.validation.iso_date(data.third_term_start)
        if third <= second:
            raise ValidationError(
                "L’inici del tercer trimestre ha de ser posterior al del segon."
            )
        determinator = AcademicCourseDeterminator()
        if (determinator.curs_academic_singular(second) != course.course
                or determinator.curs_academic_singular(third) != course.course):
            raise ValidationError(
                "Les dates dels trimestres han de pertànyer al curs acadèmic seleccionat."
            )
        return self.configuration_dao.save_term_configuration(
            TermConfigurationNew(course.id, group_name, second, third)
        )

    def delete_term_configuration(self, configuration_id: int) -> None:
        configuration_id = self.validation.positive_id(configuration_id)
        existing = next((item for item in self.get_term_configurations()
                         if item.id == configuration_id), None)
        if existing is None:
            raise EntityNotFoundError("La configuració de trimestres no existeix.")
        self.configuration_dao.delete_term_configuration(configuration_id)

    def term_for_date(self, academic_course_id: int, group_name: str,
                      date: str) -> str | None:
        self.validation.iso_date(date)
        configuration = self.get_term_configuration(academic_course_id, group_name)
        if configuration is None:
            return None
        if date < configuration.second_term_start:
            return "1r"
        if date < configuration.third_term_start:
            return "2n"
        return "3r"

    def get_ordered_categories(self) -> list[Category]:
        categories = self.categories.get_all()
        by_id = {category.id: category for category in categories}
        ordered = [by_id.pop(category_id) for category_id
                   in self.configuration_dao.get_category_order()
                   if category_id in by_id]
        ordered.extend(sorted(by_id.values(), key=lambda category: category.name.casefold()))
        return ordered

    def set_category_order(self, category_ids: list[int]) -> list[Category]:
        if not isinstance(category_ids, list) or any(
            isinstance(item, bool) or not isinstance(item, int) for item in category_ids
        ):
            raise ValidationError("L’ordre de categories no és vàlid.")
        existing_ids = {category.id for category in self.categories.get_all()}
        if len(category_ids) != len(set(category_ids)):
            raise ValidationError("Una categoria no pot aparèixer més d’una vegada.")
        if set(category_ids) != existing_ids:
            raise ValidationError("L’ordre ha d’incloure totes les categories existents.")
        with self.transaction_factory():
            self.configuration_dao.set_category_order(category_ids)
        return self.get_ordered_categories()

    def get_header_image(self) -> Path | None:
        value = self.configuration_dao.get_setting("header_image")
        if not value:
            return None
        path = Path(value)
        return path if path.is_file() else None

    def set_header_image(self, source: str | Path) -> Path:
        source = Path(source)
        if not source.is_file():
            raise ValidationError("No s’ha trobat la imatge de capçalera seleccionada.")
        try:
            Image.from_file(str(source))
        except (OSError, UnrecognizedImageError) as error:
            raise ValidationError("El fitxer seleccionat no és una imatge vàlida.") from error
        if self.storage_dir is None:
            raise ValidationError("No s’ha configurat el magatzem del logotip.")
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ValidationError("No s’ha pogut preparar el magatzem del logotip.") from error
        destination = self.storage_dir / f"report-logo-{uuid4().hex}{source.suffix.lower()}"
        previous = self.get_header_image()
        try:
            shutil.copy2(source, destination)
            self.configuration_dao.set_setting("header_image", str(destination))
        except (OSError, ReportConfigurationPersistenceError) as error:
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                LOGGER.warning(
                    "No s'ha pogut netejar el logotip nou després d'un error: %s",
                    destination,
                    exc_info=True,
                )
            raise ValidationError("No s’ha pogut desar la imatge de capçalera.") from error
        if previous and previous.parent.resolve() == self.storage_dir.resolve():
            try:
                previous.unlink(missing_ok=True)
            except OSError:
                LOGGER.warning(
                    "No s'ha pogut eliminar el logotip anterior: %s",
                    previous,
                    exc_info=True,
                )
        return destination

    def clear_header_image(self) -> None:
        previous = self.get_header_image()
        try:
            self.configuration_dao.delete_setting("header_image")
        except ReportConfigurationPersistenceError as error:
            raise ValidationError(
                "No s’ha pogut eliminar la configuració del logotip."
            ) from error
        if previous and self.storage_dir and previous.parent.resolve() == self.storage_dir.resolve():
            try:
                previous.unlink(missing_ok=True)
            except OSError:
                LOGGER.warning(
                    "No s'ha pogut eliminar el fitxer del logotip: %s",
                    previous,
                    exc_info=True,
                )
