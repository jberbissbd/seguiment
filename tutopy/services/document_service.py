import shutil
import uuid
from pathlib import Path

from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import StudentDocument, StudentDocumentNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.validation_service import ValidationService


class DocumentService:
    """API de negoci per a les metadades dels documents d'alumnes."""

    def __init__(self, document_dao: DocumentDAO, student_dao: StudentDAO,
        validation_service: ValidationService = None, storage_dir=None):
        self.document_dao = document_dao
        self.student_dao = student_dao
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
        source_path: str) -> StudentDocument:
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
            ))
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
        ))
        document.student_id = existing.student_id
        document.name = prepared.name
        document.description = prepared.description
        document.uuid_filename = existing.uuid_filename
        document.original_filename = existing.original_filename
        document.file_path = existing.file_path
        self.document_dao.update(document)
        return document

    def delete(self, document_id: int) -> StudentDocument:
        document = self.get_by_id(document_id)
        self.document_dao.delete(document_id)
        path = Path(document.file_path) if document.file_path else None
        if path and self.storage_dir:
            try:
                if path.resolve().parent == self.storage_dir.resolve():
                    path.unlink(missing_ok=True)
            except OSError:
                pass
        return document

    def _prepare(self, data: StudentDocumentNew) -> StudentDocumentNew:
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
        )

    def _require_student(self, student_id: int):
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
