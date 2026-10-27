"""Cel·la individual del pla de distribució d'aula."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QMenu, QVBoxLayout, QWidget

from tutopy.models.classroom_layout import CellType
from tutopy.models.messaging import Student
from tutopy.ui.widgets import classroom_layout_mime as mime
from tutopy.ui.widgets.avatar import avatar_stylesheet, circular_pixmap, initials

CELL_SIZE = 64
AVATAR_SIZE = 44

CELL_TYPE_LABELS = {
    CellType.EMPTY: "",
    CellType.AISLE: "···",
    CellType.TEACHER: "Professor",
}


class ClassroomCellWidget(QFrame):
    """Una cel·la de la graella: seient (buit o amb alumne), passadís, buit o professor.

    No conté cap lògica de negoci: només emet senyals quan l'usuari hi
    interactua; el controlador decideix com interpretar-les.
    """

    move_requested = Signal(int, str, int, int)
    """student_id, origen, fila de destí, columna de destí."""
    type_change_requested = Signal(int, int, str)
    """fila, columna, nou `CellType.value`."""
    teacher_place_requested = Signal(int, int)
    """fila, columna on col·locar la taula del professor."""
    return_to_pending_requested = Signal(int)
    """student_id a tornar a la llista de pendents."""

    def __init__(self, row: int, column: int, parent: QWidget | None = None):
        """Construeix una cel·la buida a la posició de model `(row, column)`."""
        super().__init__(parent)
        self.row = row
        self.column = column
        self.setObjectName("classroomCell")
        self.setFixedSize(CELL_SIZE, CELL_SIZE)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.avatar_label)

        self._cell_type = CellType.SEAT
        self._student: Student | None = None
        self.update_cell(CellType.SEAT, None, None, False)

    def update_cell(
        self, cell_type: CellType, student: Student | None, photo_path: str | None,
        show_photos: bool,
    ) -> None:
        """Actualitza l'aparença d'aquesta cel·la.

        Args:
            cell_type: Tipus de la cel·la.
            student: Alumne assignat, o `None` si la cel·la és buida.
            photo_path: Ruta de la foto de l'alumne, si en té.
            show_photos: Si cal mostrar la foto en lloc de les inicials.
        """
        self._cell_type = cell_type
        self._student = student
        self.setProperty("cellType", cell_type.value)
        self.avatar_label.setPixmap(QPixmap())
        self.avatar_label.setStyleSheet("")
        self.setToolTip("")
        if cell_type == CellType.SEAT and student is not None:
            pixmap = circular_pixmap(photo_path, AVATAR_SIZE) if show_photos and photo_path else None
            if pixmap is not None:
                self.avatar_label.setText("")
                self.avatar_label.setPixmap(pixmap)
            else:
                self.avatar_label.setText(initials(student.name, student.surnames))
                self.avatar_label.setStyleSheet(avatar_stylesheet(student.id, 18))
            self.setToolTip(student.full_name)
        else:
            self.avatar_label.setText(CELL_TYPE_LABELS.get(cell_type, ""))
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:
        """Inicia un arrossegament si la cel·la té un alumne assignat."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._cell_type == CellType.SEAT and self._student is not None
        ):
            drag = QDrag(self)
            drag.setMimeData(mime.encode(
                self._student.id, mime.cell_origin(self.row, self.column),
            ))
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mousePressEvent(event)

    def dragEnterEvent(self, event) -> None:
        """Accepta l'arrossegament d'un alumne si la cel·la és un seient."""
        if self._cell_type == CellType.SEAT and mime.decode(event.mimeData()) is not None:
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Emet `move_requested` amb l'alumne i l'origen arrossegats."""
        if self._handle_drop(event.mimeData()):
            event.acceptProposedAction()

    def _handle_drop(self, mime_data) -> bool:
        """Decodifica `mime_data` i emet `move_requested` si la cel·la és un seient.

        Separat de `dropEvent` perquè es pugui testejar sense passar per
        `QDropEvent.acceptProposedAction()`, que requereix una sessió real
        d'arrossegament de Qt i no es pot invocar de manera fiable sobre un
        esdeveniment construït a mà (hi ha un problema conegut de PySide6
        que hi provoca una violació de segment fora d'una sessió real).

        Returns:
            Si la cel·la ha acceptat el `drop` (per decidir si cridar
            `acceptProposedAction`).
        """
        if self._cell_type != CellType.SEAT:
            return False
        decoded = mime.decode(mime_data)
        if decoded is None:
            return False
        student_id, origin = decoded
        self.move_requested.emit(student_id, origin, self.row, self.column)
        return True

    def _show_menu(self, position) -> None:
        menu = QMenu(self)
        for cell_type, label in (
            (CellType.SEAT, "Seient"), (CellType.EMPTY, "Buit"),
            (CellType.AISLE, "Passadís"),
        ):
            menu.addAction(label, lambda value=cell_type.value: self.type_change_requested.emit(
                self.row, self.column, value,
            ))
        menu.addSeparator()
        menu.addAction(
            "Col·locar la taula del professor aquí",
            lambda: self.teacher_place_requested.emit(self.row, self.column),
        )
        if self._student is not None:
            menu.addSeparator()
            menu.addAction(
                "Tornar a pendents",
                lambda student_id=self._student.id: self.return_to_pending_requested.emit(
                    student_id,
                ),
            )
        menu.exec(self.mapToGlobal(position))
