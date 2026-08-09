from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import StudentDocument, StudentDocumentNew
from tutopy.services.exceptions import EntityNotFoundError
from tutopy.services.validation_service import ValidationService


class DocumentService:
    """API de negoci per a les metadades dels documents d'alumnes."""

    def __init__(self, document_dao: DocumentDAO, student_dao: StudentDAO,
        validation_service: ValidationService = None):
        self.document_dao = document_dao
        self.student_dao = student_dao
        self.validation_service = validation_service or ValidationService()

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
