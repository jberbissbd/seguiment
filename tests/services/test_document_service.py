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


def test_document_service_importa_i_elimina_fitxer_gestionat(
    document_dao, student_dao, db, tmp_path
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    source = tmp_path / "informe.pdf"
    source.write_bytes(b"contingut")
    storage = tmp_path / "documents"
    service = DocumentService(document_dao, student_dao, storage_dir=storage)

    document = service.import_file(student.id, "Informe", "", str(source))

    managed_file = storage / document.uuid_filename
    assert managed_file.read_bytes() == b"contingut"
    assert document.original_filename == "informe.pdf"
    assert source.exists()

    service.delete(document.id)

    assert not managed_file.exists()
    assert source.exists()


def test_document_service_valida_obertura_i_exporta_fitxer(
    document_dao, student_dao, db, tmp_path
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    source = tmp_path / "informe.txt"
    source.write_text("Informe", encoding="utf-8")
    service = DocumentService(
        document_dao, student_dao, storage_dir=tmp_path / "documents"
    )
    document = service.import_file(student.id, "Informe", "", str(source))
    destination = tmp_path / "exportats" / "copia.txt"

    assert service.get_readable_path(document.id).is_file()
    exported = service.export_file(document.id, str(destination))

    assert exported == destination
    assert destination.read_text(encoding="utf-8") == "Informe"


def test_document_service_rebutja_fitxer_extern_al_magatzem(
    document_dao, student_dao, db, tmp_path
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    external = tmp_path / "extern.txt"
    external.write_text("Extern", encoding="utf-8")
    service = DocumentService(
        document_dao, student_dao, storage_dir=tmp_path / "documents"
    )
    document = service.create(StudentDocumentNew(
        student.id, "Extern", "", "extern.txt", "extern.txt", str(external)
    ))

    with pytest.raises(ValidationError):
        service.get_readable_path(document.id)
