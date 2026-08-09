import pytest

from tutopy.models.messaging import StudentDocumentNew, StudentNew
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


def test_document_service_crud(document_dao, student_dao, db):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    service = DocumentService(document_dao, student_dao)
    document = service.create(StudentDocumentNew(
        student.id, " Informe ", " Descripció ", "uuid.pdf", "informe.pdf", "/tmp/informe.pdf"
    ))

    assert document.name == "Informe"
    assert service.get_by_student(student.id) == [document]
    document.name = "Informe actualitzat"
    updated = service.update(document)
    assert updated.name == "Informe actualitzat"
    assert updated.uuid_filename == "uuid.pdf"

    deleted = service.delete(document.id)
    assert deleted.file_path == "/tmp/informe.pdf"
    with pytest.raises(EntityNotFoundError):
        service.get_by_id(document.id)


def test_document_service_valida_relacions_i_nom(document_dao, student_dao, db):
    service = DocumentService(document_dao, student_dao)
    with pytest.raises(EntityNotFoundError):
        service.get_by_student(999)

    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    with pytest.raises(ValidationError):
        service.create(StudentDocumentNew(
            student.id, " ", "", "uuid.pdf", "informe.pdf"
        ))
