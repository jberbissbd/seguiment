from tutopy.models.classroom_layout import CellType, LayoutCell, LayoutGrid


def _grid(rows=3, columns=3):
    return LayoutGrid(rows, columns)


def test_assign_col_loca_un_alumne_en_una_cel_la_buida():
    grid = _grid()
    displaced = grid.assign(1, 0, 0)
    assert displaced is None
    assert grid.find(1) == (0, 0)
    assert grid.cells[(0, 0)].student_id == 1


def test_assign_mou_l_alumne_de_la_cel_la_anterior():
    grid = _grid()
    grid.assign(1, 0, 0)
    grid.assign(1, 1, 1)
    assert grid.find(1) == (1, 1)
    assert grid.cells[(0, 0)].student_id is None


def test_assign_entre_dues_cel_les_propies_retorna_l_ocupant_per_intercanviar():
    grid = _grid()
    grid.assign(1, 0, 0)
    grid.assign(2, 0, 1)
    displaced = grid.assign(1, 0, 1)
    assert displaced == 2
    assert grid.find(1) == (0, 1)
    # qui crida és responsable de completar l'intercanvi:
    grid.assign(displaced, 0, 0)
    assert grid.find(2) == (0, 0)


def test_assign_sobre_cel_la_ocupada_sense_moviment_no_fa_res():
    grid = _grid()
    grid.assign(1, 0, 0)
    displaced = grid.assign(1, 0, 0)
    assert displaced is None
    assert grid.find(1) == (0, 0)


def test_assign_des_de_pendents_retorna_l_ocupant_desplacat():
    grid = _grid()
    grid.assign(2, 0, 0)
    displaced = grid.assign(1, 0, 0)
    assert displaced == 2
    assert grid.find(1) == (0, 0)
    assert grid.find(2) is None


def test_remove_buida_la_cel_la_i_retorna_la_cel_la_anterior():
    grid = _grid()
    grid.assign(1, 1, 1)
    cell = grid.remove(1)
    assert cell.row == 1 and cell.column == 1
    assert grid.find(1) is None
    assert grid.cells[(1, 1)].student_id is None


def test_remove_alumne_no_assignat_retorna_none():
    grid = _grid()
    assert grid.remove(99) is None


def test_set_cell_type_buida_una_cel_la_ocupada_i_retorna_l_alumne():
    grid = _grid()
    grid.assign(1, 0, 0)
    displaced = grid.set_cell_type(0, 0, CellType.AISLE)
    assert displaced == 1
    assert grid.cells[(0, 0)].cell_type == CellType.AISLE
    assert grid.cells[(0, 0)].student_id is None


def test_set_cell_type_sense_alumne_no_retorna_res():
    grid = _grid()
    assert grid.set_cell_type(2, 2, CellType.EMPTY) is None


def test_resize_descarta_cel_les_fora_de_les_noves_mides_i_retorna_desplacats():
    grid = _grid(3, 3)
    grid.assign(1, 2, 2)
    grid.assign(2, 0, 0)
    displaced = grid.resize(2, 2)
    assert displaced == [1]
    assert grid.rows == 2 and grid.columns == 2
    assert (2, 2) not in grid.cells
    assert grid.find(2) == (0, 0)


def test_resize_conserva_les_cel_les_dins_dels_nous_limits():
    grid = _grid(3, 3)
    grid.cells[(1, 1)] = LayoutCell(1, 1, CellType.AISLE)
    grid.resize(2, 2)
    assert grid.cells[(1, 1)].cell_type == CellType.AISLE


def test_place_teacher_substitueix_cel_les_i_retorna_alumnes_trepitjats():
    grid = _grid(3, 4)
    grid.assign(1, 0, 2)
    displaced = grid.place_teacher(0, 2, width=2)
    assert displaced == [1]
    assert grid.cells[(0, 2)].cell_type == CellType.TEACHER
    assert grid.cells[(0, 3)].cell_type == CellType.TEACHER


def test_place_teacher_neteja_la_taula_anterior():
    grid = _grid(3, 4)
    grid.place_teacher(0, 0, width=2)
    grid.place_teacher(1, 0, width=2)
    teacher_cells = [pos for pos, cell in grid.cells.items() if cell.cell_type == CellType.TEACHER]
    assert sorted(teacher_cells) == [(1, 0), (1, 1)]


def test_place_teacher_ignora_columnes_fora_de_la_graella():
    grid = _grid(2, 3)
    displaced = grid.place_teacher(0, 2, width=2)
    assert displaced == []
    assert grid.cells[(0, 2)].cell_type == CellType.TEACHER
    assert (0, 3) not in grid.cells


def test_assigned_retorna_nomes_les_cel_les_amb_alumne():
    grid = _grid()
    grid.assign(1, 0, 0)
    grid.set_cell_type(1, 1, CellType.EMPTY)
    assigned = grid.assigned()
    assert set(assigned) == {1}
    assert assigned[1].row == 0 and assigned[1].column == 0


def test_seats_retorna_nomes_les_cel_les_de_tipus_seient():
    grid = _grid(2, 2)
    grid.set_cell_type(0, 1, CellType.AISLE)
    seats = grid.seats()
    assert len(seats) == 3
    assert all(cell.cell_type == CellType.SEAT for cell in seats)
