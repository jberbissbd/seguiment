"""Tests dels generadors de plantilles de distribució d'aula."""

import pytest

from tutopy.models.classroom_layout import CellType
from tutopy.models.classroom_layout_generators import (
    _evenly_spread_indices, generate_columns, generate_exam, generate_free_grid,
    generate_islands, generate_u_shape,
)


def _seats(grid):
    return [cell for cell in grid.cells.values() if cell.cell_type == CellType.SEAT]


def test_generate_free_grid_tot_son_seients():
    """Generate free grid tot son seients."""
    grid = generate_free_grid(2, 3)
    assert len(_seats(grid)) == 6


def test_generate_columns_exemple_del_document():
    """26 alumnes amb patró 2-3-2 donen 7 seients/fila, 4 files, 9 columnes, sense sobrants."""
    grid = generate_columns("2-3-2", 26)
    assert (grid.rows, grid.columns) == (4, 9)
    assert len(_seats(grid)) == 26


def test_generate_columns_alcada_variable_quan_les_files_son_automatiques():
    """7 alumnes amb patró "2-2" (4 seients/fila): cap seient sobrant, una columna més curta."""
    grid = generate_columns("2-2", 7)
    assert grid.rows == 2
    assert len(_seats(grid)) == 7
    # la columna més curta no té seient a la fila del fons (fila 1), però sí al davant
    short_columns = [
        column for column in range(grid.columns)
        if grid.cells[(1, column)].cell_type == CellType.EMPTY
    ]
    assert len(short_columns) == 1
    assert grid.cells[(0, short_columns[0])].cell_type == CellType.SEAT


def test_generate_columns_alcada_uniforme_quan_encaixen_exactament():
    """8 alumnes amb patró "2-2" (4 seients/fila) omplen exactament 2 files senceres."""
    grid = generate_columns("2-2", 8)
    assert grid.rows == 2
    assert len(_seats(grid)) == 8


def test_generate_columns_amb_rows_manual_mante_el_rectangle_complet():
    """Amb `rows` fixat a mà, es manté el rectangle complet (sense alçada variable)."""
    grid = generate_columns("2-2", 7, rows=3)
    assert grid.rows == 3
    assert len(_seats(grid)) == 12


def test_generate_columns_block_rows_fixa_lalcada_dun_bloc():
    """3 blocs de 2 seients: el primer amb 4 files fixes, la resta automàtic."""
    grid = generate_columns("2-2-2", 30, block_rows=[4, None, None])
    # bloc 0: 2 columnes x 4 files = 8 seients, sempre
    block_0_seats = [cell for cell in _seats(grid) if cell.block == 0]
    assert len(block_0_seats) == 8
    assert {cell.row for cell in block_0_seats} == {0, 1, 2, 3}
    # la resta (30 - 8 = 22 alumnes) es reparteix entre els blocs 1 i 2 (4 columnes)
    assert len(_seats(grid)) == 30


def test_generate_columns_block_rows_tots_els_blocs_fixats():
    """Exemple de l'usuari: 3 blocs de 2 seients, el primer de 4 files i la resta de 5."""
    grid = generate_columns("2-2-2", 100, block_rows=[4, 5, 5])
    assert len(_seats(grid)) == 2 * 4 + 2 * 5 + 2 * 5
    block_0_rows = {cell.row for cell in _seats(grid) if cell.block == 0}
    block_1_rows = {cell.row for cell in _seats(grid) if cell.block == 1}
    block_2_rows = {cell.row for cell in _seats(grid) if cell.block == 2}
    assert block_0_rows == {0, 1, 2, 3}
    assert block_1_rows == block_2_rows == {0, 1, 2, 3, 4}
    assert grid.rows == 5


def test_generate_columns_block_rows_longitud_incorrecta_rebutjada():
    """Generate columns block rows longitud incorrecta rebutjada."""
    with pytest.raises(ValueError, match="alçada"):
        generate_columns("2-2", 10, block_rows=[3])


def test_generate_columns_block_rows_valor_fora_de_rang_rebutjat():
    """Generate columns block rows valor fora de rang rebutjat."""
    with pytest.raises(ValueError, match="alçada"):
        generate_columns("2-2", 10, block_rows=[0, None])


def test_generate_columns_block_rows_amb_rows_manual_s_ignora():
    """Si `rows` és manual, es manté el rectangle complet i `block_rows` no té efecte."""
    grid = generate_columns("2-2", 10, rows=3, block_rows=[1, None])
    assert grid.rows == 3
    assert len(_seats(grid)) == 12


@pytest.mark.parametrize(("total", "count"), [(7, 5), (7, 2), (4, 1), (9, 0), (9, 9)])
def test_evenly_spread_indices_reparteix_el_nombre_exacte(total, count):
    """Evenly spread indices reparteix el nombre exacte."""
    indices = _evenly_spread_indices(total, count)
    assert len(indices) == count
    assert indices <= set(range(total))


def test_evenly_spread_indices_evita_agrupar_els_indexs():
    """Amb 2 de 7, els índexs triats no haurien de quedar junts."""
    indices = sorted(_evenly_spread_indices(7, 2))
    assert indices[1] - indices[0] > 1


def test_generate_columns_crea_passadissos_entre_blocs():
    """Generate columns crea passadissos entre blocs."""
    grid = generate_columns("2-2", 4, rows=1)
    types = [grid.cells[(0, column)].cell_type for column in range(grid.columns)]
    assert types == [
        CellType.SEAT, CellType.SEAT, CellType.AISLE, CellType.SEAT, CellType.SEAT,
    ]


def test_generate_columns_assigna_bloc_per_columna():
    """Generate columns assigna bloc per columna."""
    grid = generate_columns("2-3", 5, rows=1)
    blocks = [grid.cells[(0, column)].block for column in range(grid.columns)]
    assert blocks == [0, 0, None, 1, 1, 1]


@pytest.mark.parametrize("pattern", ["", "2-", "a-b", "2,2", "-2"])
def test_generate_columns_rebutja_patro_invalid(pattern):
    """Generate columns rebutja patró invàlid."""
    with pytest.raises(ValueError, match="patró"):
        generate_columns(pattern, 10)


def test_generate_columns_rebutja_bloc_massa_gran():
    """Generate columns rebutja bloc massa gran."""
    with pytest.raises(ValueError, match="1 i 6"):
        generate_columns("7", 10)


def test_generate_columns_rebutja_massa_columnes():
    """Generate columns rebutja massa columnes."""
    pattern = "-".join(["6"] * 5)
    with pytest.raises(ValueError, match="límit"):
        generate_columns(pattern, 100)


def test_generate_columns_sense_alumnes_dona_una_fila():
    """Generate columns sense alumnes dona una fila."""
    grid = generate_columns("2-2", 0)
    assert grid.rows == 1


def test_generate_islands_estructura_basica():
    """Generate islands estructura bàsica."""
    grid = generate_islands((2, 2), 2, 8)
    assert len(_seats(grid)) == 8
    # una sola banda (8 seients / (2 illes * 4 seients) = 1 banda)
    assert grid.rows == 2
    assert grid.columns == 5  # 2*2 + 1 passadís


def test_generate_islands_bandes_multiples_amb_passadis_entremig():
    """Generate islands bandes multiples amb passadis entremig."""
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
    """Generate islands rebutja mides invalides."""
    with pytest.raises(ValueError):
        generate_islands(island_size, islands_per_row, 10)


def test_generate_u_shape_automatic_mida():
    """Generate u shape automàtic mida."""
    grid = generate_u_shape(None, 12)
    assert grid.rows == grid.columns


def test_generate_u_shape_costats_ocupats_centre_i_davant_lliures():
    """Generate u shape costats ocupats centre i davant lliures."""
    grid = generate_u_shape(4, 0)
    assert grid.cells[(3, 0)].cell_type == CellType.SEAT  # fons-esquerra
    assert grid.cells[(3, 3)].cell_type == CellType.SEAT  # fons-dreta
    assert grid.cells[(1, 0)].cell_type == CellType.SEAT  # costat
    assert grid.cells[(1, 1)].cell_type == CellType.EMPTY  # centre
    assert grid.cells[(0, 1)].cell_type == CellType.EMPTY  # davant, obert al professor


def test_generate_u_shape_rebutja_mida_massa_petita():
    """Generate u shape rebutja mida massa petita."""
    with pytest.raises(ValueError):
        generate_u_shape(1, 0)


def test_generate_exam_cel_les_alternes_buides():
    """Generate exam cel les alternes buides."""
    grid = generate_exam(2, 2)
    assert grid.cells[(0, 0)].cell_type == CellType.SEAT
    assert grid.cells[(0, 1)].cell_type == CellType.EMPTY
    assert grid.cells[(1, 0)].cell_type == CellType.EMPTY
    assert grid.cells[(1, 1)].cell_type == CellType.SEAT
