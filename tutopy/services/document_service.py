import logging
import shutil
import uuid
from pathlib import Path

from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import StudentDocument, StudentDocumentNew
from tutopy.services.exceptions import (
    EntityNotFoundError,
    FileCleanupError,
    ValidationError,
)
from tutopy.services.validation_service import ValidationService
from tutopy.services.utils import AcademicCourseDeterminator


LOGGER = logging.getLogger(__name__)


class DocumentService:
    """API de negoci per a les metadades dels documents d'alumnes."""

    def __init__(self, document_dao: DocumentDAO, student_dao: StudentDAO,
        academic_course_dao: AcademicCourseDAO = None,
        validation_service: ValidationService = None, storage_dir=None):
        self.document_dao = document_dao
        self.student_dao = student_dao
        self.academic_course_dao = academic_course_dao
        self.validation_service = validation_service or ValidationService()
        self.storage_dir = Path(storage_dir) if storage_dir else None

    def get_all(self) -> list[StudentDocument]:
        return self.document_dao.get_all()

    def get_by_student(self, student_id: int) -> list[StudentDocument]:
        self._require_student(student_id)
        return self.document_dao.get_by_student(student_id)

    def get_by_id(self, document_id: int) -> StudentDocument:
        self.validation_service.positive_id(document_id)
        document = self.document_dao.get_by_id(document_id)
        if document is None:
            raise EntityNotFoundError(f"El document amb ID {document_id} no existeix.")
        return document

    def create(self, data: StudentDocumentNew) -> StudentDocument:
        self._require_student(data.student_id)
        return self.document_dao.create(self._prepare(data))

    def import_file(self, student_id: int, name: str, description: str,
        source_path: str, date: str = "") -> StudentDocument:
        """Copia un fitxer al magatzem gestionat i en desa les metadades."""
        self._require_student(student_id)
        if self.storage_dir is None:
            raise ValidationError("No s'ha configurat el directori de documents.")
        source = Path(source_path)
        if not source.is_file():
            raise ValidationError("El fitxer seleccionat no existeix.")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        internal_name = f"{uuid.uuid4()}{source.suffix.lower()}"
        destination = self.storage_dir / internal_name
        try:
            shutil.copy2(source, destination)
            return self.create(StudentDocumentNew(
                student_id=student_id,
                name=name,
                description=description,
                uuid_filename=internal_name,
                original_filename=source.name,
                file_path=str(destination),
                date=date,
            ))
        # La neteja s'ha d'executar davant qualsevol fallada posterior a la
        # còpia (inclòs un defecte inesperat); l'excepció original es conserva.
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def update(self, document: StudentDocument) -> StudentDocument:
        existing = self.get_by_id(document.id)
        prepared = self._prepare(StudentDocumentNew(
            student_id=existing.student_id,
            name=document.name,
            description=document.description,
            uuid_filename=existing.uuid_filename,
            original_filename=existing.original_filename,
            file_path=existing.file_path,
            date=document.date,
            course_id=document.course_id,
        ))
        document.student_id = existing.student_id
        document.name = prepared.name
        document.description = prepared.description
        document.uuid_filename = existing.uuid_filename
        document.original_filename = existing.original_filename
        document.file_path = existing.file_path
        document.date = prepared.date
        document.course_id = prepared.course_id
        self.document_dao.update(document)
        return document

    def get_readable_path(self, document_id: int) -> Path:
        """Retorna el fitxer gestionat després de validar-ne ubicació i existència."""
        document = self.get_by_id(document_id)
        if self.storage_dir is None or not document.file_path:
            raise ValidationError("El document no té cap fitxer gestionat.")
        path = Path(document.file_path)
        try:
            managed = path.resolve()
            storage = self.storage_dir.resolve()
        except OSError as error:
            raise ValidationError("No s'ha pogut localitzar el document.") from error
        if managed.parent != storage or not managed.is_file():
            raise ValidationError("El fitxer del document no existeix o no és accessible.")
        return managed

    def export_file(self, document_id: int, destination_path: str) -> Path:
        """Copia un document gestionat a una ubicació escollida per l'usuari."""
        source = self.get_readable_path(document_id)
        destination = Path(destination_path)
        if not destination.name:
            raise ValidationError("Cal indicar una destinació per exportar el document.")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source == destination.resolve():
                raise ValidationError("El document ja es troba en aquesta ubicació.")
            shutil.copy2(source, destination)
        except ValidationError:
            raise
        except OSError as error:
            raise ValidationError("No s'ha pogut exportar el document.") from error
        return destination

    def delete(self, document_id: int) -> StudentDocument:
        document = self.get_by_id(document_id)
        path = Path(document.file_path) if document.file_path else None
        quarantined = None
        if path and self.storage_dir:
            try:
                managed = path.resolve()
                if managed.parent == self.storage_dir.resolve() and managed.is_file():
                    quarantined = managed.with_name(
                        f".{managed.name}.{uuid.uuid4().hex}.deleting"
                    )
                    managed.replace(quarantined)
            except OSError as error:
                raise ValidationError(
                    "No s'ha pogut preparar el fitxer del document per eliminar-lo."
                ) from error
        try:
            self.document_dao.delete(document_id)
        except Exception:
            if quarantined is not None:
                try:
                    quarantined.replace(path)
                except OSError:
                    LOGGER.exception(
                        "No s'ha pogut restaurar el fitxer del document %s", document_id
                    )
            raise
        if quarantined is not None:
            try:
                quarantined.unlink()
            except OSError as error:
                raise FileCleanupError(
                    "El document s'ha eliminat, però no s'ha pogut esborrar "
                    "completament el fitxer associat."
                ) from error
        return document

    def _prepare(self, data: StudentDocumentNew) -> StudentDocumentNew:
        if not data.date:
            raise ValidationError("La data del document és obligatòria.")
        document_date = self.validation_service.iso_date(data.date)
        course_id = data.course_id
        if document_date:
            if self.academic_course_dao is None:
                raise ValidationError("No es pot determinar el curs acadèmic del document.")
            course_name = AcademicCourseDeterminator().curs_academic_singular(document_date)
            course_id = self.academic_course_dao.get_or_create(course_name).id
        return StudentDocumentNew(
            student_id=data.student_id,
            name=self.validation_service.required_text(
                data.name, "El nom del document no pot estar buit."
            ),
            description=self.validation_service.optional_text(data.description),
            uuid_filename=self.validation_service.required_text(
                data.uuid_filename, "El nom intern del document no pot estar buit."
            ),
            original_filename=self.validation_service.optional_text(data.original_filename),
            file_path=self.validation_service.optional_text(data.file_path),
            date=document_date,
            course_id=course_id,
        )

    def _require_student(self, student_id: int):
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
