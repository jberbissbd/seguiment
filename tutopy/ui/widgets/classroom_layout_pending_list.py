"""Llista d'alumnes del grup encara no col·locats al pla de distribució d'aula."""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QDrag, QIcon
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from tutopy.models.messaging import Student
from tutopy.ui.widgets import classroom_layout_mime as mime
from tutopy.ui.widgets.avatar import circular_pixmap

AVATAR_SIZE = 32


class PendingStudentsList(QListWidget):
    """Alumnes del grup que encara no tenen seient assignat.

    És alhora origen (arrossegar un alumne d'aquí cap a una cel·la) i destí
    (deixar-hi un alumne arrossegat des d'una cel·la el torna a pendents).
    """

    move_requested = Signal(int, str)
    """student_id, origen (sempre una cel·la quan arriba aquí)."""

    def __init__(self, parent=None):
        """Configura l'arrossegar i deixar anar en tots dos sentits."""
        super().__init__(parent)
        self.setObjectName("classroomPendingList")
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setIconSize(QSize(AVATAR_SIZE, AVATAR_SIZE))

    def set_students(
        self, students: list[Student], show_photos: bool,
        photo_paths: dict[int, str | None] | None = None,
    ) -> None:
        """Reconstrueix la llista amb els alumnes pendents indicats."""
        self.clear()
        photo_paths = photo_paths or {}
        for student in students:
            item = QListWidgetItem(student.full_name)
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            pixmap = (
                circular_pixmap(photo_paths.get(student.id), AVATAR_SIZE)
                if show_photos and photo_paths.get(student.id) else None
            )
            if pixmap is not None:
                item.setIcon(QIcon(pixmap))
            self.addItem(item)

    def startDrag(self, supported_actions) -> None:
        """Inicia l'arrossegament de l'alumne seleccionat cap a una cel·la."""
        item = self.currentItem()
        if item is None:
            return
        student_id = item.data(Qt.ItemDataRole.UserRole)
        drag = QDrag(self)
        drag.setMimeData(mime.encode(student_id, mime.PENDING_ORIGIN))
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event) -> None:
        """Accepta l'arrossegament d'un alumne des d'una cel·la."""
        if mime.decode(event.mimeData()) is not None:
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Emet `move_requested` quan un alumne arrossegat des d'una cel·la hi cau."""
        if self._handle_drop(event.mimeData()):
            event.acceptProposedAction()

    def _handle_drop(self, mime_data) -> bool:
        """Decodifica `mime_data` i emet `move_requested` si ve d'una cel·la.

        Separat de `dropEvent` pel mateix motiu que
        `ClassroomCellWidget._handle_drop`: testejable sense passar per
        `QDropEvent.acceptProposedAction()`.
        """
        decoded = mime.decode(mime_data)
        if decoded is None:
            return False
        student_id, origin = decoded
        if origin != mime.PENDING_ORIGIN:
            self.move_requested.emit(student_id, origin)
        return True
