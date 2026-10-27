"""Ompliment automàtic d'una graella, en tres etapes pures i composables.

1. `select_seats`: decideix quins seients s'utilitzen, segons el criteri
   de seients sobrants.
2. `order_seats`: ordena els seients triats (per files o per blocs).
3. `assign_in_order`: assigna una llista d'alumnes als seients ordenats,
   en l'ordre donat — l'ordre alfabètic o aleatori és responsabilitat de
   qui crida (ordenar la llista d'alumnes abans de passar-la aquí), de
   manera que el mateix mecanisme serveix per "mantenir l'ordre" en
   reaplicar una plantilla.

Cap d'aquestes funcions depèn de Qt ni de la base de dades.
"""

import random
from collections import defaultdict
from enum import Enum

from tutopy.models.classroom_layout import CellType, LayoutGrid


class LeftoverCriterion(str, Enum):
    """Criteri per decidir quins seients queden buits quan en sobren."""

    BACK = "back"
    BACK_CENTERED = "back_centered"
    SPREAD_BY_BLOCKS = "spread_by_blocks"
    FRONT = "front"
    REMOVE = "remove"


class OrderBy(str, Enum):
    """Criteri per ordenar els seients triats abans d'assignar-hi alumnes."""

    ROWS = "rows"
    BLOCKS = "blocks"


def select_seats(
    grid: LayoutGrid, count: int, criterion: LeftoverCriterion = LeftoverCriterion.BACK,
) -> list[tuple[int, int]]:
    """Retorna les posicions de seient a utilitzar per a `count` alumnes.

    Args:
        grid: Graella sobre la qual triar seients. Amb el criteri
            `REMOVE`, els seients no triats es converteixen en `EMPTY`
            directament sobre `grid` (és l'únic criteri que la muta).
        count: Nombre d'alumnes a allotjar.
        criterion: Criteri de seients sobrants a aplicar quan `count` és
            inferior al nombre de seients disponibles.

    Returns:
        Les posicions `(row, column)` triades, com a màxim `count`.
    """
    all_seats = sorted(grid.seats(), key=lambda cell: (cell.row, cell.column))
    if count >= len(all_seats):
        return [(cell.row, cell.column) for cell in all_seats]

    if criterion == LeftoverCriterion.FRONT:
        selected = all_seats[len(all_seats) - count:]
    elif criterion == LeftoverCriterion.BACK_CENTERED:
        selected = _select_back_centered(all_seats, count)
    elif criterion == LeftoverCriterion.SPREAD_BY_BLOCKS:
        selected = _select_spread_by_blocks(all_seats, count)
    elif criterion == LeftoverCriterion.REMOVE:
        selected = all_seats[:count]
        for cell in all_seats[count:]:
            grid.set_cell_type(cell.row, cell.column, CellType.EMPTY)
    else:
        selected = all_seats[:count]
    return [(cell.row, cell.column) for cell in selected]


def _select_back_centered(all_seats, count):
    """Omple files senceres des del davant; la darrera fila parcial queda centrada."""
    rows = defaultdict(list)
    for cell in all_seats:
        rows[cell.row].append(cell)
    selected = []
    remaining = count
    for row in sorted(rows):
        row_cells = sorted(rows[row], key=lambda cell: cell.column)
        if remaining >= len(row_cells):
            selected.extend(row_cells)
            remaining -= len(row_cells)
        else:
            start = (len(row_cells) - remaining) // 2
            selected.extend(row_cells[start:start + remaining])
            remaining = 0
        if remaining <= 0:
            break
    return selected


def _select_spread_by_blocks(all_seats, count):
    """Retira seients de la darrera fila de cada bloc per torns, de manera equilibrada."""
    leftover = len(all_seats) - count
    by_block = defaultdict(list)
    for cell in all_seats:
        by_block[cell.block].append(cell)
    for cells in by_block.values():
        cells.sort(key=lambda cell: (cell.row, cell.column))
    block_keys = list(by_block)
    if len(block_keys) <= 1:
        return all_seats[:count]

    removed: set[tuple[int, int]] = set()
    index = 0
    max_attempts = len(all_seats) * len(block_keys) + 1
    while len(removed) < leftover and index < max_attempts:
        block_cells = by_block[block_keys[index % len(block_keys)]]
        candidate = next(
            (cell for cell in reversed(block_cells)
             if (cell.row, cell.column) not in removed), None,
        )
        if candidate is not None:
            removed.add((candidate.row, candidate.column))
        index += 1
    return [cell for cell in all_seats if (cell.row, cell.column) not in removed]


def order_seats(
    seats: list[tuple[int, int]], grid: LayoutGrid, by: OrderBy = OrderBy.ROWS,
) -> list[tuple[int, int]]:
    """Ordena `seats` per files `(row, column)` o per blocs `(block, row, column)`."""
    if by == OrderBy.BLOCKS:
        return sorted(seats, key=lambda position: (
            grid.cells[position].block
            if grid.cells[position].block is not None else -1,
            position[0], position[1],
        ))
    return sorted(seats, key=lambda position: (position[0], position[1]))


def assign_in_order(
    grid: LayoutGrid, seats: list[tuple[int, int]], student_ids: list[int],
) -> None:
    """Assigna `student_ids` als `seats` donats, en l'ordre de totes dues llistes.

    S'atura en la llista més curta (no és un error que no coincideixin en
    longitud): és responsabilitat de qui crida decidir què fer amb els
    seients o alumnes que en sobrin.
    """
    for position, student_id in zip(seats, student_ids, strict=False):
        grid.assign(student_id, position[0], position[1])


def shuffled(student_ids: list[int], seed: int | None = None) -> list[int]:
    """Retorna una còpia de `student_ids` en un ordre aleatori."""
    shuffled_ids = list(student_ids)
    random.Random(seed).shuffle(shuffled_ids)
    return shuffled_ids
