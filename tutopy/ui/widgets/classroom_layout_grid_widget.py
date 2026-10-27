"""Graella visual de la distribució d'aula.

Únic punt d'inversió de la vista: la cel·la de model `(row, column)`, on
`row 0` és la fila del davant (la més propera al professor), es pinta
sempre a la fila de pantalla `rows_total - 1 - row`, de manera que el
professor quedi sempre a baix. Generadors, el servei i el controlador
treballen únicament amb `row 0 = davant`.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QWidget

from tutopy.models.classroom_layout import CellType, LayoutGrid
from tutopy.models.messaging import Student
from tutopy.ui.widgets.classroom_layout_cell_widget import ClassroomCellWidget


class ClassroomLayoutGridWidget(QWidget):
    """Graella de cel·les `ClassroomCellWidget`, en un `QGridLayout`."""

    move_requested = Signal(int, str, int, int)
    type_change_requested = Signal(int, int, str)
    teacher_place_requested = Signal(int, int)
    return_to_pending_requested = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        """Construeix una graella buida; cal cridar `rebuild` abans d'usar-la."""
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._layout.setSpacing(4)
        self._cells: dict[tuple[int, int], ClassroomCellWidget] = {}
        self._rows = 0

    def rebuild(
        self, grid: LayoutGrid, students_by_id: dict[int, Student],
        show_photos: bool, photo_paths: dict[int, str | None],
    ) -> None:
        """Reconstrueix totes les cel·les a partir de `grid`.

        Args:
            grid: Graella de domini a representar.
            students_by_id: Alumnes assignats, indexats per identificador.
            show_photos: Si cal mostrar fotos en lloc d'inicials.
            photo_paths: Ruta de la foto de cada alumne (pot ser `None`).
        """
        for widget in self._cells.values():
            widget.setParent(None)
            widget.deleteLater()
        self._cells = {}
        self._rows = grid.rows
        for row in range(grid.rows):
            for column in range(grid.columns):
                cell = grid.cells.get((row, column))
                cell_type = cell.cell_type if cell else CellType.SEAT
                student = (
                    students_by_id.get(cell.student_id)
                    if cell and cell.student_id is not None else None
                )
                photo_path = photo_paths.get(cell.student_id) if cell and cell.student_id else None
                widget = ClassroomCellWidget(row, column)
                widget.update_cell(cell_type, student, photo_path, show_photos)
                widget.move_requested.connect(self.move_requested)
                widget.type_change_requested.connect(self.type_change_requested)
                widget.teacher_place_requested.connect(self.teacher_place_requested)
                widget.return_to_pending_requested.connect(self.return_to_pending_requested)
                self._cells[(row, column)] = widget
                self._layout.addWidget(widget, self._display_row(row), column)

    def update_cell(
        self, row: int, column: int, cell_type: CellType, student: Student | None,
        photo_path: str | None, show_photos: bool,
    ) -> None:
        """Actualitza una sola cel·la, sense reconstruir la graella sencera."""
        widget = self._cells.get((row, column))
        if widget is not None:
            widget.update_cell(cell_type, student, photo_path, show_photos)

    def _display_row(self, row: int) -> int:
        """Converteix una fila de model en la fila de pantalla (professor a baix)."""
        return self._rows - 1 - row
