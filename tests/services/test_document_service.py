from pathlib import Path

import pytest

from tutopy.models.messaging import StudentDocumentNew, StudentNew
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import (
    EntityNotFoundError,
    FileCleanupError,
    ValidationError,
)


def test_document_service_crud(document_dao, student_dao, db):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    service = DocumentService(document_dao, student_dao, db.academic_courses)
    document = service.create(StudentDocumentNew(
        student.id, " Informe ", " Descripció ", "uuid.pdf", "informe.pdf",
        "/tmp/informe.pdf", "2026-02-01"
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
    service = DocumentService(document_dao, student_dao, db.academic_courses)
    with pytest.raises(EntityNotFoundError):
        service.get_by_student(999)

    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    invalid_document = StudentDocumentNew(
        student.id, " ", "", "uuid.pdf", "informe.pdf", "", "2026-02-01"
    )
    with pytest.raises(ValidationError):
        service.create(invalid_document)


def test_document_service_importa_i_elimina_fitxer_gestionat(
    document_dao, student_dao, db, tmp_path
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    source = tmp_path / "informe.pdf"
    source.write_bytes(b"contingut")
    storage = tmp_path / "documents"
    service = DocumentService(
        document_dao, student_dao, db.academic_courses, storage_dir=storage
    )

    document = service.import_file(student.id, "Informe", "", str(source), "2026-02-01")

    managed_file = storage / document.uuid_filename
    assert managed_file.read_bytes() == b"contingut"
    assert document.original_filename == "informe.pdf"
    assert document.date == "2026-02-01"
    assert db.academic_courses.get_by_id(document.course_id).course == "2025-2026"
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
        document_dao, student_dao, db.academic_courses,
        storage_dir=tmp_path / "documents"
    )
    document = service.import_file(student.id, "Informe", "", str(source), "2026-02-01")
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
        document_dao, student_dao, db.academic_courses,
        storage_dir=tmp_path / "documents"
    )
    document = service.create(StudentDocumentNew(
        student.id, "Extern", "", "extern.txt", "extern.txt", str(external),
        "2026-02-01"
    ))

    with pytest.raises(ValidationError):
        service.get_readable_path(document.id)


def test_document_service_avisa_si_no_pot_netejar_el_fitxer_eliminat(
    document_dao, student_dao, db, tmp_path, monkeypatch
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    source = tmp_path / "informe.txt"
    source.write_text("Informe", encoding="utf-8")
    service = DocumentService(
        document_dao, student_dao, db.academic_courses,
        storage_dir=tmp_path / "documents",
    )
    document = service.import_file(
        student.id, "Informe", "", str(source), "2026-02-01"
    )
    original_unlink = Path.unlink

    def fail_for_quarantine(path, *args, **kwargs):
        if path.name.endswith(".deleting"):
            raise OSError("fitxer bloquejat")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_for_quarantine)

    with pytest.raises(FileCleanupError, match="document s'ha eliminat"):
        service.delete(document.id)

    with pytest.raises(EntityNotFoundError):
        service.get_by_id(document.id)


def test_document_service_restaura_el_fitxer_si_falla_la_base_de_dades(
    document_dao, student_dao, db, tmp_path, monkeypatch
):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    source = tmp_path / "informe.txt"
    source.write_text("Informe", encoding="utf-8")
    service = DocumentService(
        document_dao, student_dao, db.academic_courses,
        storage_dir=tmp_path / "documents",
    )
    document = service.import_file(
        student.id, "Informe", "", str(source), "2026-02-01"
    )
    managed = Path(document.file_path)
    monkeypatch.setattr(
        document_dao,
        "delete",
        lambda _id: (_ for _ in ()).throw(RuntimeError("database unavailable")),
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.delete(document.id)

    assert managed.read_text(encoding="utf-8") == "Informe"
    assert service.get_by_id(document.id) == document
