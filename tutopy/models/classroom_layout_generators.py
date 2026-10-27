"""Generadors purs de graelles de distribució per a cada disposició.

Cada funció rep paràmetres i retorna un `LayoutGrid` nou; cap toca Qt ni
la base de dades. Validen els seus paràmetres i llancen `ValueError` amb
un missatge en català ja apte per mostrar a l'usuari (la capa que els
crida —el diàleg de plantilla— no n'ha de traduir el text).
"""

import math
import re

from tutopy.models.classroom_layout import CellType, LayoutCell, LayoutGrid

_COLUMN_PATTERN_RE = re.compile(r"^\d+(-\d+)*$")
MAX_BLOCK_SIZE = 6
MAX_GRID_SIZE = 20


def generate_free_grid(rows: int, columns: int) -> LayoutGrid:
    """Retorna una quadrícula lliure: totes les cel·les són seients."""
    return LayoutGrid(rows, columns)


def generate_columns(
    pattern: str, student_count: int, rows: int | None = None, aisle_width: int = 1,
) -> LayoutGrid:
    """Genera una graella d'agrupacions en columnes.

    Args:
        pattern: Mida de cada bloc de columnes, p. ex. `"2-3-2"`.
        student_count: Nombre d'alumnes a allotjar; determina les files si
            no se n'indica un nombre fix.
        rows: Nombre de files, o `None` per calcular-les automàticament a
            partir de `student_count`.
        aisle_width: Amplada (en columnes) del passadís entre blocs.

    Raises:
        ValueError: Si el patró no és vàlid o la graella resultant supera
            el límit de columnes.
    """
    if not _COLUMN_PATTERN_RE.match(pattern):
        raise ValueError('El patró de columnes ha de tenir el format "2-3-2".')
    blocks = [int(value) for value in pattern.split("-")]
    if any(block < 1 or block > MAX_BLOCK_SIZE for block in blocks):
        raise ValueError(f"Cada bloc ha de tenir entre 1 i {MAX_BLOCK_SIZE} seients.")
    seats_per_row = sum(blocks)
    if rows is None:
        rows = max(1, math.ceil(student_count / seats_per_row)) if student_count else 1

    column_map: list[tuple[CellType, int | None]] = []
    for block_index, size in enumerate(blocks):
        column_map += [(CellType.SEAT, block_index)] * size
        if block_index < len(blocks) - 1:
            column_map += [(CellType.AISLE, None)] * aisle_width
    columns = len(column_map)
    if columns > MAX_GRID_SIZE:
        raise ValueError(f"La disposició supera el límit de {MAX_GRID_SIZE} columnes.")

    grid = LayoutGrid(rows, columns)
    for row in range(rows):
        for column, (cell_type, block) in enumerate(column_map):
            grid.cells[(row, column)] = LayoutCell(row, column, cell_type, block)
    return grid


def generate_islands(
    island_size: tuple[int, int], islands_per_row: int, student_count: int,
) -> LayoutGrid:
    """Genera una graella de grups de treball (illes), amb passadís en totes dues direccions.

    Args:
        island_size: `(files, columnes)` de cada illa.
        islands_per_row: Nombre d'illes per filera.
        student_count: Nombre d'alumnes a allotjar; determina quantes
            fileres d'illes calen.

    Raises:
        ValueError: Si la mida de l'illa o el nombre d'illes per filera no
            és vàlid, o la graella resultant supera el límit de columnes.
    """
    island_rows, island_columns = island_size
    if island_rows < 1 or island_columns < 1:
        raise ValueError("La mida de l'illa ha de ser com a mínim 1×1.")
    if islands_per_row < 1:
        raise ValueError("Cal com a mínim una illa per filera.")

    seats_per_band = islands_per_row * island_rows * island_columns
    bands = max(1, math.ceil(student_count / seats_per_band)) if student_count else 1
    columns = islands_per_row * island_columns + (islands_per_row - 1)
    rows = bands * island_rows + (bands - 1)
    if columns > MAX_GRID_SIZE:
        raise ValueError(f"La disposició supera el límit de {MAX_GRID_SIZE} columnes.")

    grid = LayoutGrid(rows, columns)
    block_id = 0
    for band in range(bands):
        band_row_start = band * (island_rows + 1)
        block_id = _fill_island_band(
            grid, band_row_start, island_rows, island_columns, islands_per_row, block_id,
        )
        if band < bands - 1:
            aisle_row = band_row_start + island_rows
            for column in range(columns):
                grid.cells[(aisle_row, column)] = LayoutCell(aisle_row, column, CellType.AISLE)
    return grid


def _fill_island_band(
    grid: LayoutGrid, band_row_start: int, island_rows: int, island_columns: int,
    islands_per_row: int, block_id: int,
) -> int:
    """Omple una filera d'illes amb seients i els passadissos entre elles.

    Returns:
        El següent `block_id` lliure, després d'assignar-ne un a cada illa.
    """
    for island_index in range(islands_per_row):
        col_start = island_index * (island_columns + 1)
        for offset_row in range(island_rows):
            row = band_row_start + offset_row
            for offset_column in range(island_columns):
                column = col_start + offset_column
                grid.cells[(row, column)] = LayoutCell(row, column, CellType.SEAT, block_id)
            if island_index > 0:
                grid.cells[(row, col_start - 1)] = LayoutCell(
                    row, col_start - 1, CellType.AISLE,
                )
        block_id += 1
    return block_id


def generate_u_shape(seats_per_side: int | None, student_count: int) -> LayoutGrid:
    """Genera una graella en U: taules als costats i al fons, centre i davant lliures.

    Args:
        seats_per_side: Seients per costat (l'U és quadrada, de mida
            `seats_per_side × seats_per_side`), o `None` per calcular-los
            automàticament a partir de `student_count`.
        student_count: Nombre d'alumnes a allotjar, usat quan
            `seats_per_side` és `None`.

    Raises:
        ValueError: Si `seats_per_side` és inferior a 2.
    """
    if seats_per_side is None:
        seats_per_side = max(2, math.ceil(student_count / 3)) if student_count else 3
    if seats_per_side < 2:
        raise ValueError("Calen com a mínim 2 seients per costat.")

    size = seats_per_side
    grid = LayoutGrid(size, size)
    for row in range(size):
        for column in range(size):
            on_back = row == size - 1
            on_side = column in (0, size - 1)
            cell_type = CellType.SEAT if (on_back or on_side) else CellType.EMPTY
            grid.cells[(row, column)] = LayoutCell(row, column, cell_type)
    return grid


def generate_exam(rows: int, columns: int) -> LayoutGrid:
    """Genera una graella d'examen: seients individuals amb una cel·la buida entre ells."""
    grid = LayoutGrid(rows, columns)
    for row in range(rows):
        for column in range(columns):
            if (row + column) % 2 == 1:
                grid.cells[(row, column)] = LayoutCell(row, column, CellType.EMPTY)
    return grid
