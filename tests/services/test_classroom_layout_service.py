import pytest

from tutopy.models.classroom_layout import CellType, ClassroomLayoutNew
from tutopy.models.messaging import StudentNew
from tutopy.services.classroom_layout_service import ClassroomLayoutService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def service(db):
    return ClassroomLayoutService(db.classroom_layouts, db.students, db.transaction)


def test_create_layout_valida_i_crea(service):
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    assert layout.group_name == "4t A"
    assert layout.rows == 3 and layout.columns == 4


@pytest.mark.parametrize("field, value", [
    ("name", ""), ("group_name", ""),
])
def test_create_layout_rebutja_text_buit(service, field, value):
    data = ClassroomLayoutNew("4t A", "A1", 3, 4)
    kwargs = {"group_name": data.group_name, "name": data.name,
              "rows": data.rows, "columns": data.columns}
    kwargs[field] = value
    with pytest.raises(ValidationError):
        service.create_layout(ClassroomLayoutNew(**kwargs))


@pytest.mark.parametrize("rows, columns", [(0, 4), (21, 4), (4, 0), (4, 21)])
def test_create_layout_rebutja_mides_fora_de_rang(service, rows, columns):
    with pytest.raises(ValidationError):
        service.create_layout(ClassroomLayoutNew("4t A", "A1", rows, columns))


def test_create_layout_rebutja_mode_o_posicio_invalids(service):
    with pytest.raises(ValidationError):
        service.create_layout(
            ClassroomLayoutNew("4t A", "A1", 3, 4, teacher_mode="volant")
        )
    with pytest.raises(ValidationError):
        service.create_layout(
            ClassroomLayoutNew("4t A", "A1", 3, 4, teacher_position="amunt")
        )


def test_load_buida_cel_les_d_alumnes_que_ja_no_son_del_grup(service, db):
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
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 2, 2))
    seated = db.students.create(StudentNew("Laia", "Serra", "4t A"))
    unseated = db.students.create(StudentNew("Pau", "Font", "4t A"))
    _, grid, _ = service.load(layout.id)
    grid.assign(seated.id, 0, 0)
    service.save(layout, grid)

    _, _, pending = service.load(layout.id)
    assert [student.id for student in pending] == [unseated.id]


def test_load_distribucio_inexistent_llanca_error(service):
    with pytest.raises(EntityNotFoundError):
        service.load(999)


def test_save_substitueix_totes_les_cel_les(service, db):
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
    first = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    second = service.create_layout(ClassroomLayoutNew("4t A", "A2", 3, 4))
    service.set_active(first.id)
    service.set_active(second.id)
    assert service.get_active("4t A").id == second.id


def test_delete_elimina_la_distribucio(service, db):
    layout = service.create_layout(ClassroomLayoutNew("4t A", "A1", 3, 4))
    service.delete(layout.id)
    assert db.classroom_layouts.get_by_id(layout.id) is None
