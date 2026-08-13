from openpyxl import load_workbook
from datetime import date
import pytest
import unicodedata

from tutopy.application import create_services
from tutopy.models.messaging import (
    CategoryNew, NoteNew, StudentGroupHistoryNew, StudentNew,
)
from tutopy.models.reporting import TermConfigurationNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


def _report_scenario(db, tmp_path):
    services = create_services(db)
    student = db.students.create(StudentNew("Laia", "Martí", "4t B"))
    academic = db.categories.create(CategoryNew("Acadèmic"))
    family = db.categories.create(CategoryNew("Família"))
    conduct = db.categories.create(CategoryNew("Conducta"))
    services.report_configuration.set_category_order([
        academic.id, family.id, conduct.id,
    ])
    course = db.academic_courses.get_or_create("2025-2026")
    db.student_group_history.create(StudentGroupHistoryNew(
        student.id, "4t A", "2025-09-01", "2026-02-01", course.id
    ))
    db.student_group_history.create(StudentGroupHistoryNew(
        student.id, "4t B", "2026-02-01", None, course.id
    ))
    services.report_configuration.save_term_configuration(TermConfigurationNew(
        course.id, "4t A", "2026-01-08", "2026-04-07"
    ))
    services.report_configuration.save_term_configuration(TermConfigurationNew(
        course.id, "4t B", "2026-01-10", "2026-04-10"
    ))
    for category, note_date, content in (
        (family, "2025-09-15", "Entrevista inicial"),
        (academic, "2026-01-15", "Bona evolució"),
        (conduct, "2026-02-10", "Incidència resolta"),
        (academic, "2026-04-15", "Objectius assolits"),
    ):
        services.notes.create(NoteNew(student.id, category.id, note_date, 0, content))
    return services, student, (academic, family, conduct), tmp_path / "informe.xlsx"


def test_exporta_full_per_curs_amb_categories_i_grup_historic(db, tmp_path):
    services, student, _categories, destination = _report_scenario(db, tmp_path)
    path = services.spreadsheet_reports.export_student(
        student.id, destination, include_terms=True
    )
    workbook = load_workbook(path)
    assert workbook.sheetnames == ["2025-2026"]
    sheet = workbook["2025-2026"]
    assert sheet["A1"].value == "Martí, Laia — 4t A, 4t B"
    assert sheet["A2"].value == (
        f"Data d’exportació: {date.today().strftime('%d/%m/%Y')}"
    )
    assert [sheet.cell(3, column).value for column in range(1, 6)] == [
        "Trimestre", "Grup", "Acadèmic", "Família", "Conducta"
    ]
    assert sheet["A4"].value == "1r"
    assert sheet["B4"].value == "4t A"
    assert sheet["D4"].value == "15/09/2025 - Entrevista inicial"
    assert sheet["C5"].value == "15/01/2026 - Bona evolució"
    assert sheet["B6"].value == "4t B"
    assert sheet["E6"].value == "10/02/2026 - Incidència resolta"
    assert sheet["C7"].value == "15/04/2026 - Objectius assolits"
    assert "A5:A6" in {str(area) for area in sheet.merged_cells.ranges}
    assert sheet.freeze_panes == "A4"


def test_exportacio_sense_trimestres_no_crea_la_columna(db, tmp_path):
    services, student, _categories, _destination = _report_scenario(db, tmp_path)
    path = services.spreadsheet_reports.export_student(
        student.id, tmp_path / "sense-trimestres", include_terms=False
    )
    sheet = load_workbook(path).active
    assert path.suffix == ".xlsx"
    assert [sheet.cell(3, column).value for column in range(1, 5)] == [
        "Grup", "Acadèmic", "Família", "Conducta"
    ]
    assert not any(str(area).startswith("A4:A") for area in sheet.merged_cells.ranges)


def test_crea_un_full_per_curs_en_ordre_ascendent(db, tmp_path):
    services, student, categories, destination = _report_scenario(db, tmp_path)
    services.notes.create(NoteNew(
        student.id, categories[0].id, "2024-10-01", 0, "Curs anterior"
    ))
    workbook = load_workbook(services.spreadsheet_reports.export_student(
        student.id, destination
    ))
    assert workbook.sheetnames == ["2024-2025", "2025-2026"]


def test_rebutja_alumne_inexistent_o_sense_notes(db, tmp_path):
    services = create_services(db)
    with pytest.raises(EntityNotFoundError):
        services.spreadsheet_reports.export_student(999, tmp_path / "x.xlsx")
    student = services.students.create(StudentNew("Pau", "Puig", "3r A"))
    with pytest.raises(ValidationError, match="no té notes"):
        services.spreadsheet_reports.export_student(student.id, tmp_path / "x.xlsx")


def test_saneja_unicode_controls_formules_i_longitud(db, tmp_path):
    services = create_services(db)
    decomposed_name = unicodedata.normalize("NFD", "Júlia")
    student = services.students.create(StudentNew(decomposed_name, "Nuñez 😊", "4t\x00 A"))
    category = services.categories.create(CategoryNew("=HYPERLINK(\"x\")"))
    long_content = "Evolució\x07 positiva 😊 " + ("à" * 40_000)
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, long_content
    ))
    sheet = load_workbook(services.spreadsheet_reports.export_student(
        student.id, tmp_path / "unicode.xlsx"
    )).active
    assert sheet["A1"].value.startswith("Nuñez 😊, Júlia — 4t A")
    assert "\x00" not in sheet["A1"].value
    assert sheet["B3"].value == '=HYPERLINK("x")'
    assert sheet["B3"].data_type == "s"
    assert "\x07" not in sheet["B4"].value
    assert "😊" in sheet["B4"].value
    assert len(sheet["B4"].value) == 32_767
    assert sheet["B4"].data_type == "s"
