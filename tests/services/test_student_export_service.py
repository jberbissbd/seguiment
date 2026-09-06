from datetime import date
from pathlib import Path

import pytest

from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


@pytest.mark.parametrize("available", [True, False], ids=["adjunt-present", "adjunt-absent"])
def test_informe_fallit_recupera_adjunts_sense_ocultar_error_original(
    db, managed_document, tmp_path, available,
):
    """Sense notes, el lot informa de la fallada i conserva els adjunts recuperables."""
    document_service, document, _source = managed_document
    services = create_services(db)
    services.documents.storage_dir = document_service.storage_dir
    if not available:
        document_service.get_readable_path(document.id).unlink()
    result = services.student_exports.export_students(
        [document.student_id], tmp_path / "lots", "xlsx", include_documents=True,
    )
    assert result.exported == 0
    assert len(result.failures) == 1
    assert "no té notes" in result.failures[0].reason
    recovered = list(Path(result.destination).rglob("*.txt"))
    assert len(recovered) == int(available)
    if available:
        assert recovered[0].read_text() == "Document original"


@pytest.mark.parametrize("batch", [False, True], ids=["individual", "lot"])
def test_destinacio_bloquejada_informa_sense_alterar_fitxers(
    db, managed_document, tmp_path, batch,
):
    """Una destinació que és un fitxer no es reemplaça ni amaga l'error del sistema."""
    _service, document, _source = managed_document
    destination = tmp_path / "destinacio.txt"
    destination.write_text("No substituir", encoding="utf-8")
    exporter = create_services(db).student_exports
    with pytest.raises(ValidationError, match="carpeta d’exportació") as error:
        if batch:
            exporter.export_students([document.student_id], destination, "xlsx")
        else:
            exporter.export_student(document.student_id, destination, "xlsx")
    assert isinstance(error.value.__cause__, OSError)
    assert destination.read_text() == "No substituir"


def test_exportacio_individual_rebutja_alumne_absent(db, tmp_path):
    """L'exportació d'un alumne inexistent no crea cap carpeta."""
    destination = tmp_path / "exportacio"
    with pytest.raises(EntityNotFoundError, match="no existeix"):
        create_services(db).student_exports.export_student(99999, destination, "xlsx")
    assert not destination.exists()


def test_exportacio_individual_rebutja_destinacio_buida(db, managed_document):
    """Una destinació buida no s'interpreta com el directori de treball."""
    _service, document, _source = managed_document
    with pytest.raises(ValidationError, match="destinació"):
        create_services(db).student_exports.export_student(document.student_id, "", "xlsx")


def test_exporta_informe_i_documents_en_carpetes_per_curs(db, tmp_path):
    services = create_services(db)
    services.documents.storage_dir = tmp_path / "managed"
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Bona evolució"
    ))
    first = tmp_path / "primer.pdf"
    second = tmp_path / "segon.txt"
    first.write_bytes(b"PDF")
    second.write_text("Text", encoding="utf-8")
    services.documents.import_file(
        student.id, "Informe", "Valoració", str(first), "2026-02-03"
    )
    services.documents.import_file(
        student.id, "Acta", "Valoració", str(second), "2024-10-10"
    )

    root = services.student_exports.export_student(
        student.id, tmp_path / "exportacio", "xlsx"
    )

    assert root == tmp_path / "exportacio" / "Martí, Laia"
    assert (root / "informe.xlsx").is_file()
    assert (root / "2025-2026" / "Valoració.pdf").read_bytes() == b"PDF"
    assert (root / "2024-2025" / "Valoració.txt").read_text(encoding="utf-8") == "Text"


def test_exporta_diversos_alumnes_i_separa_homonims(db, tmp_path):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Acadèmic"))
    first = services.students.create(StudentNew("Alex", "Garcia", "2n A"))
    second = services.students.create(StudentNew("Alex", "Garcia", "2n B"))
    for student in (first, second):
        services.notes.create(NoteNew(
            student.id, category.id, "2026-02-01", 0, "Seguiment"
        ))

    result = services.student_exports.export_students(
        [first.id, second.id], tmp_path / "lots", "docx"
    )
    root = tmp_path / "lots" / f"Informes {date.today().isoformat()}"
    assert result.destination == str(root)
    assert result.exported == 2
    assert result.failures == ()
    assert (root / "Garcia, Alex" / "informe.docx").is_file()
    assert (root / "Garcia, Alex (2)" / "informe.docx").is_file()


def test_exportacio_multiple_continua_si_un_alumne_no_te_notes(db, tmp_path):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Acadèmic"))
    valid = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    empty = services.students.create(StudentNew("Pau", "Puig", "3r A"))
    services.notes.create(NoteNew(
        valid.id, category.id, "2026-02-01", 0, "Seguiment"
    ))

    result = services.student_exports.export_students(
        [empty.id, valid.id], tmp_path / "lots", "xlsx"
    )
    assert result.exported == 1
    assert len(result.failures) == 1
    assert result.failures[0].student_name == "Puig, Pau"


@pytest.mark.parametrize("student_ids", [[], [0], [True], [1, 1], "1"])
def test_exportacio_multiple_rebutja_seleccions_invalides(
    db, tmp_path, student_ids
):
    service = create_services(db).student_exports

    with pytest.raises(ValidationError, match="seleccionar|selecció"):
        service.export_students(student_ids, tmp_path / "lots", "xlsx")


def test_exportacio_rebutja_format_i_destinacio_invalids(db, tmp_path):
    services = create_services(db)

    with pytest.raises(ValidationError, match="format"):
        services.student_exports.export_students(
            [1], tmp_path / "lots", "html"
        )
    with pytest.raises(ValidationError, match="destinació"):
        services.student_exports.export_students([1], "", "xlsx")


def test_exportacio_multiple_informa_alumne_inexistent(db, tmp_path):
    result = create_services(db).student_exports.export_students(
        [999], tmp_path / "lots", "xlsx"
    )

    assert result.exported == 0
    assert result.failures[0].student_id == 999
    assert result.failures[0].student_name == "ID 999"


def test_noms_de_carpeta_son_segurs_i_disponibles(tmp_path):
    from tutopy.services.student_export_service import StudentExportService

    assert StudentExportService._safe_name('  <A/B>:*  ', "Alumne") == "A_B"
    assert StudentExportService._safe_name("...", "Alumne") == "Alumne"
    original = tmp_path / "Informe"
    original.mkdir()
    (tmp_path / "Informe (2)").mkdir()
    assert StudentExportService._available_path(original).name == "Informe (3)"


def test_exportacio_preparada_es_pot_cancel_lar_entre_alumnes(db, tmp_path):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Seguiment"))
    student_ids = []
    for index in range(3):
        student = services.students.create(
            StudentNew(f"Nom {index}", "Cognom", "1A")
        )
        services.notes.create(
            NoteNew(student.id, category.id, "2026-02-01", 0, "Seguiment")
        )
        student_ids.append(student.id)
    preparation = services.student_exports.prepare_students_export(
        student_ids, tmp_path / "lots", "xlsx"
    )
    progress = []

    result = services.student_exports.export_prepared(
        preparation,
        progress_callback=lambda completed, total: progress.append((completed, total)),
        cancel_requested=lambda: bool(progress),
    )

    assert result.cancelled is True
    assert result.exported == 1
    assert progress == [(1, 3)]
