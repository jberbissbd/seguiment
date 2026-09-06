from dataclasses import replace
from pathlib import Path
import shutil

import pytest

from tutopy.models.messaging import StudentDocumentNew, StudentNew
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import (
    EntityNotFoundError,
    FileCleanupError,
    ValidationError,
)


def test_importacio_invalida_neteja_copia_i_conserva_original(managed_document):
    """La validació fallida després de copiar no deixa fitxers orfes."""
    service, document, source = managed_document
    with pytest.raises(ValidationError):
        service.import_file(document.student_id, " ", "", str(source), "2026-02-01")
    assert list(service.storage_dir.iterdir()) == [Path(document.file_path)]
    assert service.get_all() == [document]
    assert source.read_text() == "Document original"


@pytest.mark.parametrize("failure", ["storage", "source"])
def test_importacio_rebutja_magatzem_o_origen_absents(managed_document, failure):
    """Els requisits absents no creen registres de documents."""
    service, document, source = managed_document
    if failure == "storage":
        service.storage_dir = None
    else:
        source.unlink()
    with pytest.raises(ValidationError, match="directori|no existeix"):
        service.import_file(document.student_id, "Informe", "", str(source), "2026-02-01")
    assert service.get_all() == [document]


@pytest.mark.parametrize("destination", ["", "same"])
def test_exportacio_rebutja_destinacio_buida_o_original(managed_document, destination):
    """Exportar sobre l'original o sense ruta no altera el document gestionat."""
    service, document, _source = managed_document
    target = document.file_path if destination == "same" else destination
    with pytest.raises(ValidationError, match="destinació|aquesta ubicació"):
        service.export_file(document.id, target)
    assert Path(document.file_path).read_text() == "Document original"


def test_exportacio_tradueix_error_de_copia(managed_document, tmp_path, monkeypatch):
    """Un error del sistema de fitxers es converteix en un error de domini."""
    service, document, _source = managed_document

    def denied(*args):
        raise PermissionError("destinació protegida")

    monkeypatch.setattr(shutil, "copy2", denied)
    with pytest.raises(ValidationError, match="exportar") as error:
        service.export_file(document.id, str(tmp_path / "copia.txt"))
    assert isinstance(error.value.__cause__, PermissionError)
    assert Path(document.file_path).read_text() == "Document original"


def test_error_preparant_eliminacio_conserva_registre_i_fitxer(managed_document, monkeypatch):
    """La impossibilitat de moure a quarantena impedeix esborrar les metadades."""
    service, document, _source = managed_document

    def denied(*args):
        raise PermissionError("fitxer protegit")

    monkeypatch.setattr(Path, "replace", denied)
    with pytest.raises(ValidationError, match="preparar el fitxer"):
        service.delete(document.id)
    assert service.get_by_id(document.id) == document
    assert Path(document.file_path).read_text() == "Document original"


def test_error_restituint_quarantena_conserva_copia_i_error_original(
    managed_document, monkeypatch, caplog,
):
    """Una restauració fallida registra el problema i preserva el fitxer recuperable."""
    service, document, _source = managed_document
    original_replace = Path.replace

    def fail_restore(path, destination):
        if path.name.endswith(".deleting"):
            raise PermissionError("restauració bloquejada")
        return original_replace(path, destination)

    def fail_delete(_document_id):
        raise RuntimeError("base de dades no disponible")

    monkeypatch.setattr(Path, "replace", fail_restore)
    monkeypatch.setattr(service.document_dao, "delete", fail_delete)
    with pytest.raises(RuntimeError, match="base de dades no disponible"):
        service.delete(document.id)
    assert service.get_by_id(document.id) == document
    backups = list(service.storage_dir.glob("*.deleting"))
    assert len(backups) == 1
    assert backups[0].read_text() == "Document original"
    assert "No s'ha pogut restaurar" in caplog.text


def test_eliminar_metadades_externes_no_esborra_fitxer(managed_document):
    """L'eliminació d'un registre no toca fitxers que són fora del magatzem."""
    service, document, source = managed_document
    external = service.create(StudentDocumentNew(
        document.student_id, "Extern", "", "extern.txt", source.name, str(source), "2026-02-01",
    ))
    service.delete(external.id)
    assert source.read_text() == "Document original"
    assert service.get_all() == [document]


def test_consulta_per_lots_rebutja_alumne_inexistent(managed_document):
    """Una selecció amb alumnes inexistents no retorna un lot parcial."""
    service, document, _source = managed_document
    with pytest.raises(EntityNotFoundError, match="99999"):
        service.get_by_students([document.student_id, 99999])


@pytest.mark.parametrize("failure", ["date", "courses"])
def test_metadades_requereixen_data_i_cataleg_de_cursos(managed_document, failure):
    """No es desa cap document amb data absent o sense poder determinar el curs."""
    service, document, _source = managed_document
    if failure == "courses":
        service.academic_course_dao = None
    with pytest.raises(ValidationError, match="data|curs acadèmic"):
        service.create(StudentDocumentNew(
            document.student_id, "Informe", "", "nou.txt", "nou.txt", "",
            "" if failure == "date" else "2026-02-01",
        ))
    assert service.get_all() == [document]


def test_document_service_crud(document_dao, student_dao, db):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    service = DocumentService(document_dao, student_dao, db.academic_courses)
    document = service.create(StudentDocumentNew(
        student.id, " Informe ", " Descripció ", "uuid.pdf", "informe.pdf",
        "/tmp/informe.pdf", "2026-02-01"
    ))

    assert document.name == "Informe"
    assert service.get_by_student(student.id) == [document]
    document = replace(document, name="Informe actualitzat")
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
