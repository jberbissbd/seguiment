from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.report_configuration_dao import ReportConfigurationDAO
from tutopy.models.messaging import Category
from tutopy.models.reporting import TermConfiguration, TermConfigurationNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.utils import AcademicCourseDeterminator
from tutopy.services.validation_service import ValidationService


class ReportConfigurationService:
    """Preferències persistents per generar els informes de seguiment."""

    def __init__(self, configuration_dao: ReportConfigurationDAO,
                 courses: AcademicCourseDAO, categories: CategoryDAO,
                 transaction_factory, validation_service: ValidationService = None):
        self.configuration_dao = configuration_dao
        self.courses = courses
        self.categories = categories
        self.transaction_factory = transaction_factory
        self.validation = validation_service or ValidationService()

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
