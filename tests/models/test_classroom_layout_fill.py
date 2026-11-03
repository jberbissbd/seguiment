"""Tests de l'ompliment automàtic de la graella de distribució d'aula."""

from tutopy.models.classroom_layout import CellType, LayoutGrid
from tutopy.models.classroom_layout_fill import (
    Direction, LeftoverCriterion, OrderBy, assign_in_order, order_seats, select_seats, shuffled,
)
from tutopy.models.classroom_layout_generators import generate_columns


def test_select_seats_amb_prou_capacitat_retorna_tots():
    """Select seats amb prou capacitat retorna tots."""
    grid = LayoutGrid(1, 3)
    selected = select_seats(grid, 5, LeftoverCriterion.BACK)
    assert set(selected) == {(0, 0), (0, 1), (0, 2)}


def test_select_seats_back_deixa_el_final_de_la_darrera_fila_buit():
    """Select seats back deixa el final de la darrera fila buit."""
    grid = LayoutGrid(2, 3)
    selected = select_seats(grid, 4, LeftoverCriterion.BACK)
    assert set(selected) == {(0, 0), (0, 1), (0, 2), (1, 0)}


def test_select_seats_front_deixa_la_primera_fila_lliure():
    """Select seats front deixa la primera fila lliure."""
    grid = LayoutGrid(2, 3)
    selected = select_seats(grid, 3, LeftoverCriterion.FRONT)
    assert set(selected) == {(1, 0), (1, 1), (1, 2)}


def test_select_seats_remove_buida_els_no_triats():
    """Select seats remove buida els no triats."""
    grid = LayoutGrid(1, 4)
    select_seats(grid, 2, LeftoverCriterion.REMOVE)
    types = [grid.cells[(0, column)].cell_type for column in range(4)]
    assert types == [CellType.SEAT, CellType.SEAT, CellType.EMPTY, CellType.EMPTY]


def test_select_seats_back_centered_centra_la_darrera_fila_parcial():
    """Select seats back centered centra la darrera fila parcial."""
    grid = LayoutGrid(2, 4)
    selected = select_seats(grid, 6, LeftoverCriterion.BACK_CENTERED)
    # fila 0 (davant) sencera (4), fila 1 (fons) amb 2 centrats
    assert {position for position in selected if position[0] == 0} == {
        (0, 0), (0, 1), (0, 2), (0, 3),
    }
    back_row_selected = {position for position in selected if position[0] == 1}
    assert back_row_selected == {(1, 1), (1, 2)}


def test_select_seats_spread_by_blocks_equilibra_entre_blocs():
    """Select seats spread by blocks equilibra entre blocs."""
    grid = generate_columns("2-2", 4, rows=2)
    selected = select_seats(grid, 6, LeftoverCriterion.SPREAD_BY_BLOCKS)
    assert len(selected) == 6
    block_0_selected = sum(
        1 for position in selected if grid.cells[position].block == 0
    )
    block_1_selected = sum(
        1 for position in selected if grid.cells[position].block == 1
    )
    assert block_0_selected == 3
    assert block_1_selected == 3


def test_order_seats_per_files():
    """Order seats per files."""
    seats = [(1, 0), (0, 1), (0, 0)]
    grid = LayoutGrid(2, 2)
    assert order_seats(seats, grid, OrderBy.ROWS) == [(0, 0), (0, 1), (1, 0)]


def test_order_seats_per_blocs():
    """Order seats per blocs."""
    grid = generate_columns("2-2", 4, rows=1)
    seats = [(0, 3), (0, 0), (0, 1), (0, 4)]
    ordered = order_seats(seats, grid, OrderBy.BLOCKS)
    blocks = [grid.cells[position].block for position in ordered]
    assert blocks == sorted(blocks)


def test_order_seats_per_columnes_dins_del_bloc_des_de_lesquerra():
    """Order seats per columnes dins del bloc des de l'esquerra."""
    grid = LayoutGrid(2, 3)
    seats = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    ordered = order_seats(seats, grid, OrderBy.COLUMNS, Direction.LEFT)
    assert ordered == [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]


def test_order_seats_per_columnes_dins_del_bloc_des_de_la_dreta():
    """Order seats per columnes dins del bloc des de la dreta."""
    grid = LayoutGrid(2, 3)
    seats = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    ordered = order_seats(seats, grid, OrderBy.COLUMNS, Direction.RIGHT)
    assert ordered == [(0, 2), (1, 2), (0, 1), (1, 1), (0, 0), (1, 0)]


def test_order_seats_per_columnes_respecta_els_blocs():
    """Order seats per columnes respecta els blocs."""
    grid = generate_columns("2-2", 4, rows=2)
    seats = [(cell.row, cell.column) for cell in grid.seats()]
    ordered = order_seats(seats, grid, OrderBy.COLUMNS, Direction.LEFT)
    blocks = [grid.cells[position].block for position in ordered]
    assert blocks == sorted(blocks)


def test_assign_in_order_assigna_per_parelles():
    """Assign in order assigna per parelles."""
    grid = LayoutGrid(1, 3)
    assign_in_order(grid, [(0, 0), (0, 1), (0, 2)], [11, 22])
    assert grid.find(11) == (0, 0)
    assert grid.find(22) == (0, 1)
    assert grid.cells[(0, 2)].student_id is None


def test_shuffled_conserva_el_mateix_conjunt():
    """Shuffled conserva el mateix conjunt."""
    ids = list(range(1, 21))
    result = shuffled(ids, seed=1)
    assert sorted(result) == ids
    assert result != ids  # amb 20 elements, pràcticament impossible que surti igual


def test_shuffled_es_determinista_amb_la_mateixa_llavor():
    """Shuffled és determinista amb la mateixa llavor."""
    ids = list(range(1, 11))
    first_result = shuffled(ids, seed=7)
    second_result = shuffled(ids, seed=7)
    assert first_result == second_result
