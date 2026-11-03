"""Esquema simplificat de la forma d'una distribució, sense alumnes.

A diferència de `ClassroomLayoutGridWidget` (cel·les reals, amb nom i
foto), aquest widget només dibuixa la forma: un quadrat per seient, un
buit pels passadissos i un bloc per la taula del professor, escalat
automàticament per ocupar l'espai disponible. Es fa servir a la
previsualització del diàleg de plantilla, on interessa veure de cop com
quedarà l'aula, no qui seurà on.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from tutopy.models.classroom_layout import CellType, LayoutGrid
from tutopy.ui.styles import BORDER_COLOR
from tutopy.ui.widgets.classroom_layout_cell_widget import SEAT_BACKGROUND, SEAT_BORDER, TEACHER_BACKGROUND

CELL_GAP = 3
# Un passadís ocupa la meitat de l'amplada d'una columna normal, igual que
# a la graella real (`AISLE_WIDTH` a classroom_layout_cell_widget.py).
AISLE_WEIGHT = 0.5


def _column_weights(grid: LayoutGrid) -> list[float]:
    """Amplada relativa de cada columna: `AISLE_WEIGHT` si és un passadís, `1.0` si no.

    Una columna de passadís ho és a totes les files (els generadors no en
    barregen mai amb altres tipus), així que n'hi ha prou de mirar-ne la
    fila 0.
    """
    return [
        AISLE_WEIGHT if grid.cells[(0, column)].cell_type == CellType.AISLE else 1.0
        for column in range(grid.columns)
    ]


class ClassroomLayoutSchematicWidget(QWidget):
    """Dibuix esquemàtic (seients/passadís/buit/professor) escalat a l'espai disponible."""

    def __init__(self, parent: QWidget | None = None):
        """Construeix el widget, inicialment sense cap graella a mostrar."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(160, 160)
        self._grid: LayoutGrid | None = None
        self._leftover_seats: frozenset[tuple[int, int]] = frozenset()

    def set_grid(
        self, grid: LayoutGrid | None,
        leftover_seats: frozenset[tuple[int, int]] = frozenset(),
    ) -> None:
        """Mostra `grid`; els seients de `leftover_seats` es dibuixen amb vora discontínua."""
        self._grid = grid
        self._leftover_seats = leftover_seats
        self.update()

    def paintEvent(self, event) -> None:
        """Dibuixa l'esquema de l'aula sobre el widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._grid is not None and self._grid.rows and self._grid.columns:
            self._paint_grid(painter)
        painter.end()

    def _paint_grid(self, painter: QPainter) -> None:
        grid = self._grid
        rows, columns = grid.rows, grid.columns
        column_weights = _column_weights(grid)
        total_weight = sum(column_weights) or columns
        unit_size = min(self.width() / total_weight, self.height() / rows)
        offset_x = (self.width() - unit_size * total_weight) / 2
        offset_y = (self.height() - unit_size * rows) / 2
        column_x = []
        x = offset_x
        for weight in column_weights:
            column_x.append(x)
            x += weight * unit_size

        for (row, column), cell in grid.cells.items():
            display_row = rows - 1 - row
            cell_width = column_weights[column] * unit_size
            rect = QRectF(
                column_x[column] + CELL_GAP / 2,
                offset_y + display_row * unit_size + CELL_GAP / 2,
                cell_width - CELL_GAP, unit_size - CELL_GAP,
            )
            self._paint_cell(painter, rect, cell.cell_type, (row, column) in self._leftover_seats)

    def _paint_cell(
        self, painter: QPainter, rect: QRectF, cell_type: CellType, is_leftover: bool,
    ) -> None:
        if cell_type == CellType.AISLE:
            return  # el passadís es dibuixa com un buit entre blocs, sense cap forma
        if cell_type == CellType.SEAT:
            painter.setBrush(QColor(SEAT_BACKGROUND))
            pen = QPen(QColor(SEAT_BORDER), 1.2)
            if is_leftover:
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
        elif cell_type == CellType.TEACHER:
            painter.setBrush(QColor(TEACHER_BACKGROUND))
            painter.setPen(Qt.PenStyle.NoPen)
        else:  # EMPTY: terra lliure dins l'aula
            painter.setBrush(QColor(BORDER_COLOR))
            painter.setPen(Qt.PenStyle.NoPen)
        radius = min(rect.width(), rect.height()) * 0.25
        painter.drawRoundedRect(rect, radius, radius)
