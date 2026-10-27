"""Model de domini per a la distribució de taules d'una aula.

`LayoutGrid` és un objecte de domini pur (sense Qt) amb comportament, no un
dataclass congelat: les mutacions (assignar, canviar tipus, redimensionar)
es fan in situ perquè el controlador les pugui aplicar una a una sense
reconstruir tota la graella a cada acció de l'usuari.
"""

from dataclasses import dataclass
from enum import Enum


class CellType(str, Enum):
    """Tipus d'una cel·la de la graella de distribució."""

    SEAT = "seat"
    EMPTY = "empty"
    AISLE = "aisle"
    TEACHER = "teacher"


@dataclass(frozen=True)
class LayoutCell:
    """Cel·la de la graella de distribució.

    Attributes:
        row: Fila, on `0` és la fila del davant (la més propera al
            professor).
        column: Columna, on `0` és l'esquerra del professor.
        cell_type: Tipus de la cel·la.
        block: Bloc o agrupació a la qual pertany (no s'utilitza a la
            fase 1; reservat per a disposicions futures).
        student_id: Alumne assignat a la cel·la, si n'hi ha.
    """

    row: int
    column: int
    cell_type: CellType
    block: int | None = None
    student_id: int | None = None


class LayoutGrid:
    """Graella mutable de cel·les d'una distribució, amb les operacions d'edició.

    Totes les operacions són pures (sense Qt) i treballen amb `row 0` com a
    fila del davant; és responsabilitat exclusiva del widget de graella
    invertir l'ordre visual perquè el professor quedi sempre a baix.
    """

    def __init__(self, rows: int, columns: int, cells: dict[tuple[int, int], LayoutCell] = None):
        """Inicialitza la graella: totes les cel·les són seients buits per defecte.

        Si es passa `cells`, només se sobreescriuen les posicions indicades;
        la resta es queden com a seients buits (quadrícula lliure, tal com
        especifica la fase 1).
        """
        self.rows = rows
        self.columns = columns
        self.cells: dict[tuple[int, int], LayoutCell] = {
            (row, column): LayoutCell(row, column, CellType.SEAT)
            for row in range(rows) for column in range(columns)
        }
        self.cells.update(cells or {})

    def assign(self, student_id: int, row: int, column: int) -> int | None:
        """Assigna `student_id` a `(row, column)`.

        Si l'alumne ja ocupava una altra cel·la d'aquesta graella, la buida
        abans d'assignar-lo a la nova. No decideix què fer amb l'ocupant
        desplaçat de la cel·la de destí (intercanvi o retorn a pendents);
        això és responsabilitat de qui crida aquest mètode.

        Returns:
            L'identificador de l'alumne que ocupava `(row, column)` abans
            d'aquesta crida, o `None` si la cel·la era buida.
        """
        origin = self.find(student_id)
        if origin is not None and origin != (row, column):
            origin_cell = self.cells[origin]
            self.cells[origin] = LayoutCell(
                origin_cell.row, origin_cell.column, origin_cell.cell_type,
                origin_cell.block, None,
            )
        cell = self.cells.get((row, column))
        if cell is None:
            cell = LayoutCell(row, column, CellType.SEAT)
        displaced = cell.student_id if cell.student_id != student_id else None
        self.cells[(row, column)] = LayoutCell(
            cell.row, cell.column, cell.cell_type, cell.block, student_id,
        )
        return displaced

    def remove(self, student_id: int) -> LayoutCell | None:
        """Buida la cel·la que ocupa `student_id`, si n'hi ha.

        Returns:
            La cel·la (ja buidada) on estava l'alumne, o `None` si no
            estava assignat enlloc.
        """
        origin = self.find(student_id)
        if origin is None:
            return None
        cell = self.cells[origin]
        emptied = LayoutCell(cell.row, cell.column, cell.cell_type, cell.block, None)
        self.cells[origin] = emptied
        return emptied

    def set_cell_type(self, row: int, column: int, cell_type: CellType) -> int | None:
        """Canvia el tipus de `(row, column)`, buidant-la si té un alumne.

        Returns:
            L'identificador de l'alumne desplaçat, si n'hi havia.
        """
        cell = self.cells.get((row, column))
        displaced = cell.student_id if cell else None
        block = cell.block if cell else None
        self.cells[(row, column)] = LayoutCell(row, column, cell_type, block, None)
        return displaced

    def resize(self, rows: int, columns: int) -> list[int]:
        """Redimensiona la graella, descartant les cel·les que en queden fora.

        Returns:
            Els identificadors dels alumnes que ocupaven cel·les eliminades.
        """
        displaced = [
            cell.student_id
            for (row, column), cell in self.cells.items()
            if (row >= rows or column >= columns) and cell.student_id is not None
        ]
        self.cells = {
            position: cell for position, cell in self.cells.items()
            if position[0] < rows and position[1] < columns
        }
        self.rows, self.columns = rows, columns
        return displaced

    def place_teacher(self, row: int, column: int, width: int = 2) -> list[int]:
        """Col·loca la taula del professor a `(row, column)`, ample `width`.

        Substitueix les cel·les que trepitja (dins els límits de la
        graella) pel tipus `TEACHER`, després de netejar qualsevol altra
        cel·la `TEACHER` existent.

        Returns:
            Els identificadors dels alumnes desplaçats per la taula.
        """
        displaced = []
        for (row_key, column_key), cell in list(self.cells.items()):
            if cell.cell_type == CellType.TEACHER:
                self.cells[(row_key, column_key)] = LayoutCell(
                    row_key, column_key, CellType.SEAT, None, None,
                )
        for offset in range(width):
            target = (row, column + offset)
            if not (0 <= target[0] < self.rows and 0 <= target[1] < self.columns):
                continue
            cell = self.cells.get(target)
            if cell and cell.student_id is not None:
                displaced.append(cell.student_id)
            self.cells[target] = LayoutCell(target[0], target[1], CellType.TEACHER)
        return displaced

    def find(self, student_id: int) -> tuple[int, int] | None:
        """Retorna la posició `(row, column)` de `student_id`, o `None`."""
        for position, cell in self.cells.items():
            if cell.student_id == student_id:
                return position
        return None

    def assigned(self) -> dict[int, LayoutCell]:
        """Retorna el mapa `student_id -> cel·la` de tots els alumnes assignats."""
        return {
            cell.student_id: cell for cell in self.cells.values()
            if cell.student_id is not None
        }

    def seats(self) -> list[LayoutCell]:
        """Retorna totes les cel·les de tipus `SEAT`."""
        return [cell for cell in self.cells.values() if cell.cell_type == CellType.SEAT]


@dataclass(frozen=True)
class ClassroomLayout:
    """Distribució desada de taules d'un grup.

    Attributes:
        id: Identificador únic.
        group_name: Grup al qual pertany la distribució.
        name: Nom visible (p. ex. "1r trimestre").
        rows: Nombre de files de la graella.
        columns: Nombre de columnes de la graella.
        teacher_mode: `"strip"` (franja fora de la graella) o `"grid"`
            (taula dins la graella, com a cel·les `TEACHER`).
        teacher_position: Alineació de la franja (`"left"`, `"center"`,
            `"right"`); només rellevant en mode `"strip"`.
        show_photos: Si cal mostrar la foto de l'alumne en lloc de les
            inicials a les cel·les ocupades.
        is_active: Si és la distribució activa d'aquest grup.
        created_at: Data de creació (`YYYY-MM-DD`).
        updated_at: Data de l'última modificació (`YYYY-MM-DD`).
    """

    id: int
    group_name: str
    name: str
    rows: int
    columns: int
    teacher_mode: str
    teacher_position: str
    show_photos: bool
    is_active: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ClassroomLayoutNew:
    """Dades d'entrada per crear una nova distribució.

    Attributes:
        group_name: Grup al qual pertany la distribució.
        name: Nom visible.
        rows: Nombre de files de la graella.
        columns: Nombre de columnes de la graella.
        teacher_mode: `"strip"` o `"grid"`.
        teacher_position: Alineació de la franja del professor.
        show_photos: Si cal mostrar fotos en lloc d'inicials.
    """

    group_name: str
    name: str
    rows: int
    columns: int
    teacher_mode: str = "strip"
    teacher_position: str = "center"
    show_photos: bool = False
