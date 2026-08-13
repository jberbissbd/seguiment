from odf import table, text, teletype
from odf.opendocument import load
import pytest

from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.services.exceptions import ValidationError


def _scenario(db):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Bona evolució"
    ))
    return services, student


def test_exporta_odt_amb_contingut_estructurat(db, tmp_path):
    services, student = _scenario(db)
    path = services.open_document_reports.export_student(
        student.id, tmp_path / "informe", "odt"
    )

    document = load(str(path))
    all_text = " ".join(
        teletype.extractText(item)
        for item in document.getElementsByType(text.P)
    )
    assert path.suffix == ".odt"
    assert "Martí, Laia" in all_text
    assert "Acadèmic" in all_text
    assert "Bona evolució" in all_text
    assert len(document.getElementsByType(table.Table)) == 1


def test_exporta_pdf_valid(db, tmp_path):
    services, student = _scenario(db)
    path = services.open_document_reports.export_student(
        student.id, tmp_path / "informe", "pdf"
    )
    assert path.read_bytes().startswith(b"%PDF-")
    assert path.stat().st_size > 1_000


def test_rebutja_format_de_document_desconegut(db, tmp_path):
    services, student = _scenario(db)
    with pytest.raises(ValidationError, match="format"):
        services.open_document_reports.export_student(
            student.id, tmp_path / "informe", "html"
        )
