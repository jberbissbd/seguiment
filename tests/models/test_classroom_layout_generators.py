import pytest

from tutopy.models.classroom_layout import CellType
from tutopy.models.classroom_layout_generators import (
    generate_columns, generate_exam, generate_free_grid, generate_islands,
    generate_u_shape,
)


def _seats(grid):
    return [cell for cell in grid.cells.values() if cell.cell_type == CellType.SEAT]


def test_generate_free_grid_tot_son_seients():
    grid = generate_free_grid(2, 3)
    assert len(_seats(grid)) == 6


def test_generate_columns_exemple_del_document():
    """26 alumnes amb patró 2-3-2 donen 7 seients/fila, 4 files, 9 columnes."""
    grid = generate_columns("2-3-2", 26)
    assert (grid.rows, grid.columns) == (4, 9)
    assert len(_seats(grid)) == 28


def test_generate_columns_crea_passadissos_entre_blocs():
    grid = generate_columns("2-2", 4, rows=1)
    types = [grid.cells[(0, column)].cell_type for column in range(grid.columns)]
    assert types == [
        CellType.SEAT, CellType.SEAT, CellType.AISLE, CellType.SEAT, CellType.SEAT,
    ]


def test_generate_columns_assigna_bloc_per_columna():
    grid = generate_columns("2-3", 5, rows=1)
    blocks = [grid.cells[(0, column)].block for column in range(grid.columns)]
    assert blocks == [0, 0, None, 1, 1, 1]


@pytest.mark.parametrize("pattern", ["", "2-", "a-b", "2,2", "-2"])
def test_generate_columns_rebutja_patro_invalid(pattern):
    with pytest.raises(ValueError, match="patró"):
        generate_columns(pattern, 10)


def test_generate_columns_rebutja_bloc_massa_gran():
    with pytest.raises(ValueError, match="1 i 6"):
        generate_columns("7", 10)


def test_generate_columns_rebutja_massa_columnes():
    with pytest.raises(ValueError, match="límit"):
        generate_columns("-".join(["6"] * 5), 100)


def test_generate_columns_sense_alumnes_dona_una_fila():
    grid = generate_columns("2-2", 0)
    assert grid.rows == 1


def test_generate_islands_estructura_basica():
    grid = generate_islands((2, 2), 2, 8)
    assert len(_seats(grid)) == 8
    # una sola banda (8 seients / (2 illes * 4 seients) = 1 banda)
    assert grid.rows == 2
    assert grid.columns == 5  # 2*2 + 1 passadís


def test_generate_islands_bandes_multiples_amb_passadis_entremig():
    grid = generate_islands((2, 2), 1, 10)
    # 10 alumnes, 4 seients per banda -> 3 bandes -> 6 files illa + 2 passadís
    assert grid.rows == 8
    aisle_rows = {
        row for row in range(grid.rows)
        if all(grid.cells[(row, column)].cell_type == CellType.AISLE
               for column in range(grid.columns))
    }
    assert len(aisle_rows) == 2


@pytest.mark.parametrize("island_size, islands_per_row", [((0, 2), 2), ((2, 2), 0)])
def test_generate_islands_rebutja_mides_invalides(island_size, islands_per_row):
    with pytest.raises(ValueError):
        generate_islands(island_size, islands_per_row, 10)


def test_generate_u_shape_automatic_mida():
    grid = generate_u_shape(None, 12)
    assert grid.rows == grid.columns


def test_generate_u_shape_costats_ocupats_centre_i_davant_lliures():
    grid = generate_u_shape(4, 0)
    assert grid.cells[(3, 0)].cell_type == CellType.SEAT  # fons-esquerra
    assert grid.cells[(3, 3)].cell_type == CellType.SEAT  # fons-dreta
    assert grid.cells[(1, 0)].cell_type == CellType.SEAT  # costat
    assert grid.cells[(1, 1)].cell_type == CellType.EMPTY  # centre
    assert grid.cells[(0, 1)].cell_type == CellType.EMPTY  # davant, obert al professor


def test_generate_u_shape_rebutja_mida_massa_petita():
    with pytest.raises(ValueError):
        generate_u_shape(1, 0)


def test_generate_exam_cel_les_alternes_buides():
    grid = generate_exam(2, 2)
    assert grid.cells[(0, 0)].cell_type == CellType.SEAT
    assert grid.cells[(0, 1)].cell_type == CellType.EMPTY
    assert grid.cells[(1, 0)].cell_type == CellType.EMPTY
    assert grid.cells[(1, 1)].cell_type == CellType.SEAT
