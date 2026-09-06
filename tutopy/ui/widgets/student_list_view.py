"""Model i dibuix de la llista d'alumnes sense widgets per fila."""

from collections.abc import Sequence

from PySide6.QtCore import QAbstractListModel, QModelIndex, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QListView, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QToolButton,
)

from tutopy.models.messaging import Student
from tutopy.ui.resources import icon
from tutopy.ui.styles import TEXT_PRIMARY, TEXT_SECONDARY
from tutopy.ui.widgets.avatar import avatar_colors, initials


class StudentListModel(QAbstractListModel):
    """Desa els alumnes i permet localitzar-los per identificador."""

    StudentRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent=None):
        """Inicialitza un model buit."""
        super().__init__(parent)
        self._students: tuple[Student, ...] = ()
        self._rows: dict[int, int] = {}

    def rowCount(self, parent=None) -> int:
        """Retorna el nombre d'alumnes del nivell arrel."""
        return 0 if parent is not None and parent.isValid() else len(self._students)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Retorna el text accessible, l'identificador o les dades de l'alumne."""
        if not index.isValid() or not 0 <= index.row() < len(self._students):
            return None
        student = self._students[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.AccessibleTextRole,
                    Qt.ItemDataRole.ToolTipRole):
            return f"{student.full_name} · {student.group_name or 'Sense grup'}"
        if role == Qt.ItemDataRole.UserRole:
            return student.id
        if role == self.StudentRole:
            return student
        return None

    def set_students(self, students: Sequence[Student]) -> None:
        """Actualitza només les dades modificades si es conserva l'ordre."""
        students = tuple(students)
        if tuple(self._rows) == tuple(student.id for student in students):
            previous = self._students
            self._students = students
            for row, (old, new) in enumerate(zip(previous, students, strict=True)):
                if old != new:
                    index = self.index(row)
                    self.dataChanged.emit(index, index)
            return
        self.beginResetModel()
        self._students = students
        self._rows = {student.id: row for row, student in enumerate(students)}
        self.endResetModel()

    def student_index(self, student_id: int | None) -> QModelIndex:
        """Retorna l'índex de l'alumne, o un índex invàlid si no hi és."""
        row = self._rows.get(student_id)
        return self.index(row) if row is not None else QModelIndex()


class StudentDelegate(QStyledItemDelegate):
    """Dibuixa l'avatar, el nom i el grup només per a les files visibles."""

    def sizeHint(self, option, index) -> QSize:
        """Reserva una alçada uniforme adaptada a la font."""
        return QSize(180, max(52, option.fontMetrics.height() * 2 + 14))

    def paint(self, painter: QPainter, option, index) -> None:
        """Pinta una fila amb el fons i el focus proporcionats per Qt."""
        student = index.data(StudentListModel.StudentRole)
        style_option = QStyleOptionViewItem(option)
        self.initStyleOption(style_option, index)
        style_option.text = ""
        option.widget.style().drawControl(
            QStyle.ControlElement.CE_ItemViewItem, style_option, painter, option.widget
        )
        painter.save()
        painter.setClipRect(option.rect)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        avatar = QRect(option.rect.left() + 8, option.rect.center().y() - 18, 36, 36)
        background, foreground = avatar_colors(student.id)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(background))
        painter.drawEllipse(avatar)
        font = QFont(option.font)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(foreground))
        painter.drawText(avatar, Qt.AlignmentFlag.AlignCenter, initials(student.name, student.surnames))
        text_rect = option.rect.adjusted(54, 6, -50, -6)
        text_rect.setHeight(text_rect.height() // 2)
        painter.setPen(QColor(TEXT_PRIMARY))
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignVCenter,
            QFontMetrics(font).elidedText(student.full_name, Qt.TextElideMode.ElideRight,
                                         max(0, text_rect.width())),
        )
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(TEXT_SECONDARY))
        text_rect.translate(0, text_rect.height())
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignVCenter,
            QFontMetrics(font).elidedText(student.group_name or "Sense grup",
                                         Qt.TextElideMode.ElideRight,
                                         max(0, text_rect.width())),
        )
        painter.restore()


class StudentListView(QListView):
    """Mostra files virtualitzades i dos botons reutilitzables de notes."""

    note_requested = Signal(int)

    def __init__(self, parent=None):
        """Configura el dibuix i les accions de la fila activa i la del cursor."""
        super().__init__(parent)
        self.setModel(StudentListModel(self))
        self.setItemDelegate(StudentDelegate(self))
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._hovered = QModelIndex()
        self.selected_note_button = self._note_button()
        self.hover_note_button = self._note_button()
        self.entered.connect(self._hover)
        self.model().modelReset.connect(self._reset_hover)

    def _note_button(self) -> QToolButton:
        button = QToolButton(self.viewport())
        button.setObjectName("studentNoteButton")
        button.setIcon(icon("add.svg"))
        button.setIconSize(QSize(16, 16))
        button.setToolTip("Afegir una nota")
        button.setAccessibleName("Afegir una nota")
        button.setAutoRaise(True)
        button.setFixedSize(34, 34)
        button.clicked.connect(lambda: self.note_requested.emit(button.property("student_id")))
        button.hide()
        return button

    def _hover(self, index) -> None:
        self._hovered = index
        self._update_buttons()

    def _reset_hover(self) -> None:
        self._hovered = QModelIndex()
        self._update_buttons()

    def _position_button(self, button, index) -> None:
        rect = self.visualRect(index) if index.isValid() else QRect()
        visible = index.isValid() and self.viewport().rect().intersects(rect)
        if visible:
            button.move(rect.right() - 42, rect.center().y() - 17)
            button.setProperty("student_id", index.data(Qt.ItemDataRole.UserRole))
        button.setVisible(visible)

    def _update_buttons(self) -> None:
        if not hasattr(self, "selected_note_button"):
            return
        self._position_button(self.selected_note_button, self.currentIndex())
        hovered = self._hovered if self._hovered != self.currentIndex() else QModelIndex()
        self._position_button(self.hover_note_button, hovered)

    def currentChanged(self, current, previous) -> None:
        """Mou el botó accessible quan canvia la selecció, també amb el teclat."""
        super().currentChanged(current, previous)
        self._update_buttons()

    def mouseMoveEvent(self, event) -> None:
        """Actualitza l'acció contextual, incloent l'espai buit de la llista."""
        super().mouseMoveEvent(event)
        self._hover(self.indexAt(event.position().toPoint()))

    def leaveEvent(self, event) -> None:
        """Amaga l'acció contextual en sortir de la llista."""
        super().leaveEvent(event)
        self._reset_hover()

    def resizeEvent(self, event) -> None:
        """Recol·loca els botons quan canvia l'amplada de la vista."""
        super().resizeEvent(event)
        self._update_buttons()

    def scrollContentsBy(self, dx, dy) -> None:
        """Recol·loca els botons i descarta la fila anterior del cursor."""
        super().scrollContentsBy(dx, dy)
        self._reset_hover()
