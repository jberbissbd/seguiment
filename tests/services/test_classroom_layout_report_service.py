import pytest

from tutopy.models.classroom_layout import CellType, ClassroomLayout
from tutopy.models.classroom_layout_generators import generate_columns
from tutopy.models.messaging import Student
from tutopy.services.classroom_layout_report_service import ClassroomLayoutReportService
from tutopy.services.exceptions import ValidationError


def _layout(**overrides):
    defaults = {
        "id": 1, "group_name": "1r A", "name": "1r trimestre", "rows": 2,
        "columns": 2, "teacher_mode": "strip", "teacher_position": "center",
        "show_photos": False, "is_active": True, "created_at": "2026-01-01",
        "updated_at": "2026-11-20",
    }
    defaults.update(overrides)
    return ClassroomLayout(**defaults)


@pytest.fixture
def service():
    return ClassroomLayoutReportService()


def test_exporta_pdf_valid(service, tmp_path):
    grid = generate_columns("2-2", 4, rows=2)
    students = {}
    for index, cell in enumerate(grid.seats(), start=1):
        students[index] = Student(index, f"u{index}", f"Nom{index}", f"Cognoms{index}", "1r A")
        grid.assign(index, cell.row, cell.column)

    path = service.export_pdf(_layout(), grid, students, tmp_path / "pla")

    assert path.suffix == ".pdf"
    assert path.read_bytes().startswith(b"%PDF-")
    assert path.stat().st_size > 500


def test_exporta_amb_taula_del_professor_dins_la_graella(service, tmp_path):
    grid = generate_columns("2-2", 2, rows=2)
    grid.set_cell_type(0, 0, CellType.TEACHER)
    grid.assign(1, 0, 1)
    students = {1: Student(1, "u1", "Nom", "Cognoms", "1r A")}

    path = service.export_pdf(
        _layout(teacher_mode="grid"), grid, students, tmp_path / "examen.pdf",
    )

    assert path.read_bytes().startswith(b"%PDF-")


def test_normalitza_lextensio_a_pdf(service, tmp_path):
    grid = generate_columns("2", 0, rows=1)
    path = service.export_pdf(_layout(), grid, {}, tmp_path / "sense_extensio")
    assert path.suffix == ".pdf"


def test_destinacio_sense_nom_de_fitxer_es_rebutjada(service):
    grid = generate_columns("2", 0, rows=1)
    with pytest.raises(ValidationError):
        service.export_pdf(_layout(), grid, {}, "")


def test_column_weights_els_passadissos_valen_la_meitat(service):
    grid = generate_columns("2-2", 4, rows=1)
    assert service._column_weights(grid) == [1.0, 1.0, 0.5, 1.0, 1.0]
