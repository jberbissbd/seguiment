"""Tests del servei de distribució d'aula."""

import pytest

from tutopy.models.classroom_layout import CellType, ClassroomLayoutNew
from tutopy.models.messaging import StudentNew
from tutopy.services.classroom_layout_service import ClassroomLayoutService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def service(db):
    """Construeix el servei de distribució d'aula sobre la base de dades de prova."""
    return ClassroomLayoutService(db.classroom_layouts, db.students, db.transaction)


def test_create_layout_valida_i_crea(service):
    """Create layout vàlida i crea."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    assert layout.group_name == "4t A"
    assert layout.rows == 3
    assert layout.columns == 4


@pytest.mark.parametrize("field, value", [
    ("name", ""), ("group_name", ""),
])
def test_create_layout_rebutja_text_buit(service, field, value):
    """Create layout rebutja text buit."""
    data = ClassroomLayoutNew("4t A", "A1", 3, 4)
    kwargs = {"group_name": data.group_name, "name": data.name,
              "rows": data.rows, "columns": data.columns}
    kwargs[field] = value
    data = ClassroomLayoutNew(**kwargs)
    with pytest.raises(ValidationError):
        service.create_layout(data)


@pytest.mark.parametrize("rows, columns", [(0, 4), (21, 4), (4, 0), (4, 21)])
def test_create_layout_rebutja_mides_fora_de_rang(service, rows, columns):
    """Create layout rebutja mides fora de rang."""
    data = ClassroomLayoutNew("4t A", "A1", rows, columns)
    with pytest.raises(ValidationError):
        service.create_layout(data)


def test_create_layout_rebutja_mode_o_posicio_invalids(service):
    """Create layout rebutja mode o posició invàlids."""
    invalid_mode = ClassroomLayoutNew("4t A", "A1", 3, 4, teacher_mode="volant")
    with pytest.raises(ValidationError):
        service.create_layout(invalid_mode)
    invalid_position = ClassroomLayoutNew("4t A", "A1", 3, 4, teacher_position="amunt")
    with pytest.raises(ValidationError):
        service.create_layout(invalid_position)


def test_load_buida_cel_les_d_alumnes_que_ja_no_son_del_grup(service, db):
    """Load buida cel les d'alumnes que ja no son del grup."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 2, 2))
    student = db.students.create(StudentNew("Laia", "Serra", "4t A"))
    other_group_student = db.students.create(StudentNew("Pau", "Font", "4t B"))
    _, grid, _ = service.load(layout.id)
    grid.assign(student.id, 0, 0)
    grid.assign(other_group_student.id, 0, 1)
    service.save(layout, grid)

    _, reloaded_grid, pending = service.load(layout.id)
    assert reloaded_grid.find(student.id) == (0, 0)
    assert reloaded_grid.find(other_group_student.id) is None
    assert reloaded_grid.cells[(0, 1)].student_id is None
    assert pending == []


def test_load_calcula_pendents_correctament(service, db):
    """Load calcula pendents correctament."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 2, 2))
    seated = db.students.create(StudentNew("Laia", "Serra", "4t A"))
    unseated = db.students.create(StudentNew("Pau", "Font", "4t A"))
    _, grid, _ = service.load(layout.id)
    grid.assign(seated.id, 0, 0)
    service.save(layout, grid)

    _, _, pending = service.load(layout.id)
    assert [student.id for student in pending] == [unseated.id]


def test_load_distribucio_inexistent_llanca_error(service):
    """Load distribució inexistent llanca error."""
    with pytest.raises(EntityNotFoundError):
        service.load(999)


def test_save_substitueix_totes_les_cel_les(service, db):
    """Save substitueix totes les cel les."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 2, 2))
    student = db.students.create(StudentNew("Laia", "Serra", "4t A"))
    _, grid, _ = service.load(layout.id)
    grid.assign(student.id, 0, 0)
    service.save(layout, grid)

    _, grid2, _ = service.load(layout.id)
    grid2.remove(student.id)
    grid2.set_cell_type(1, 1, CellType.AISLE)
    service.save(layout, grid2)

    cells = db.classroom_layouts.get_cells(layout.id)
    assert len(cells) == 4
    by_position = {(cell.row, cell.column): cell for cell in cells}
    assert by_position[(0, 0)].student_id is None
    assert by_position[(1, 1)].cell_type == CellType.AISLE


def test_set_active_desmarca_l_anterior_del_mateix_grup(service):
    """Set active desmarca l'anterior del mateix grup."""
    first = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    second = service.create_layout(ClassroomLayoutNew("4t A", "A2", 3, 4))
    service.set_active(first.id)
    service.set_active(second.id)
    assert service.get_active("4t A").id == second.id


def test_delete_elimina_la_distribucio(service, db):
    """Delete elimina la distribució."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    service.delete(layout.id)
    assert db.classroom_layouts.get_by_id(layout.id) is None


def test_duplicate_copia_la_forma_sense_els_alumnes(service, db):
    """Duplicate copia la forma sense els alumnes."""
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 2, 2))
    student = db.students.create(StudentNew("Laia", "Serra", "4t A"))
    _, grid, _ = service.load(layout.id)
    grid.assign(student.id, 0, 0)
    grid.set_cell_type(1, 1, CellType.AISLE)
    service.save(layout, grid)

    copy = service.duplicate(layout.id, "A1 (còpia)")
    assert copy.id != layout.id
    assert copy.name == "A1 (còpia)"
    assert copy.group_name == layout.group_name
    assert copy.rows == layout.rows
    assert copy.columns == layout.columns

    copy_cells = db.classroom_layouts.get_cells(copy.id)
    assert all(cell.student_id is None for cell in copy_cells)
    by_position = {(cell.row, cell.column): cell for cell in copy_cells}
    assert by_position[(1, 1)].cell_type == CellType.AISLE
