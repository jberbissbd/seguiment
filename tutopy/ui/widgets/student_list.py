"""Llista d'alumnes amb cerca, selecció i accions massives.

Mostra els alumnes en una `QListWidget` amb files personalitzades
(`StudentListItem`), permet cercar-los amb debounce i emet senyals per
crear, editar, eliminar o exportar-ne, sense consultar cap servei
directament.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QToolButton, QVBoxLayout, QWidget,
)

from tutopy.ui.resources import icon, set_button_icon

from tutopy.ui.widgets.avatar import avatar_stylesheet, initials
from tutopy.ui.widgets.debounced_line_edit import DebouncedLineEdit


class StudentListItem(QWidget):
    """Representació reutilitzable d'un alumne dins la llista."""

    note_requested = Signal(int)

    def __init__(self, student, parent=None):
        """Construeix la fila (avatar, nom, grup i botó de nota) per a `student`.

        Args:
            student: Alumne a representar.
            parent: Widget pare de Qt.
        """
        super().__init__(parent)
        self.setMinimumHeight(52)
        self._student_id = student.id
        self._hovered = False
        self._selected = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        self.avatar = QLabel(initials(student.name, student.surnames))
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFixedSize(36, 36)
        self.avatar.setStyleSheet(avatar_stylesheet(student.id, 18))
        layout.addWidget(self.avatar)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        self.name = QLabel(student.full_name)
        self.name.setObjectName("studentListName")
        self.group = QLabel(student.group_name or "Sense grup")
        self.group.setObjectName("studentListGroup")
        text_layout.addWidget(self.name)
        text_layout.addWidget(self.group)
        layout.addLayout(text_layout, 1)
        self.note_button = QToolButton()
        self.note_button.setObjectName("studentNoteButton")
        self.note_button.setIcon(icon("add.svg"))
        self.note_button.setIconSize(QSize(16, 16))
        self.note_button.setToolTip("Afegir una nota")
        self.note_button.setAccessibleName("Afegir una nota")
        self.note_button.setAutoRaise(True)
        self.note_button.setFixedSize(34, 34)
        self.note_button.clicked.connect(self._request_note)
        self.note_button.hide()
        layout.addWidget(self.note_button)

    def update_student(self, student) -> None:
        """Actualitza el contingut sense reconstruir l'arbre de widgets."""
        self.avatar.setText(initials(student.name, student.surnames))
        self.avatar.setStyleSheet(avatar_stylesheet(student.id, 18))
        self.name.setText(student.full_name)
        self.group.setText(student.group_name or "Sense grup")
        self._student_id = student.id

    def set_selected(self, selected: bool) -> None:
        """Manté l'acció visible per a la fila activa, també sense ratolí."""
        self._selected = selected
        self._update_note_button()

    def enterEvent(self, event) -> None:
        """Mostra el botó de nota mentre el ratolí és sobre la fila."""
        self._hovered = True
        self._update_note_button()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Amaga el botó de nota quan el ratolí surt de la fila (si no és la seleccionada)."""
        self._hovered = False
        self._update_note_button()
        super().leaveEvent(event)

    def _update_note_button(self) -> None:
        self.note_button.setVisible(self._hovered or self._selected)

    def _request_note(self) -> None:
        self.note_requested.emit(self._student_id)


class StudentList(QFrame):
    """Llista visual d'alumnes; no consulta directament cap servei.

    Inclou un camp de cerca amb debounce de 180 ms (`DebouncedLineEdit`) que
    emet `search_changed` un cop l'usuari deixa d'escriure.
    """

    student_selected = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)
    search_changed = Signal(str)
    create_requested = Signal()
    batch_export_requested = Signal()
    bulk_edit_requested = Signal()
    note_create_requested = Signal(int)

    def __init__(self, parent=None):
        """Construeix la capçalera d'accions, el cercador i la llista d'alumnes."""
        super().__init__(parent)
        self.setObjectName("panel")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Alumnes")
        title.setObjectName("sectionTitle")
        self.create_button = QPushButton("Nou alumne")
        set_button_icon(self.create_button, "add")
        self.create_button.setObjectName("primaryButton")
        self.create_button.clicked.connect(self.create_requested)
        header.addWidget(title)
        header.addStretch()
        header_actions = QVBoxLayout()
        header_actions.setContentsMargins(0, 0, 0, 0)
        header_actions.setSpacing(6)
        self.batch_export_button = QPushButton("Exportar diversos…")
        set_button_icon(self.batch_export_button, "export")
        self.batch_export_button.setObjectName("secondaryButton")
        self.batch_export_button.setEnabled(False)
        self.batch_export_button.clicked.connect(self.batch_export_requested)
        self.bulk_edit_button = QPushButton("Edició massiva…")
        set_button_icon(self.bulk_edit_button, "edit")
        self.bulk_edit_button.setObjectName("secondaryButton")
        self.bulk_edit_button.setEnabled(False)
        self.bulk_edit_button.clicked.connect(self.bulk_edit_requested)
        header_actions.addWidget(self.create_button)
        header_actions.addWidget(self.bulk_edit_button)
        header_actions.addWidget(self.batch_export_button)
        header.addLayout(header_actions)
        layout.addLayout(header)

        self.search_input = DebouncedLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.debounced_text_changed.connect(self.search_changed)
        layout.addWidget(self.search_input)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar")
        set_button_icon(self.edit_button, "edit")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
        set_button_icon(self.delete_button, "delete")
        self.delete_button.setObjectName("dangerButton")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.edit_button.clicked.connect(self._request_edit)
        self.delete_button.clicked.connect(self._request_delete)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("studentListWidget")
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.currentItemChanged.connect(self._emit_selection)
        self.list_widget.itemDoubleClicked.connect(
            lambda item: self.edit_requested.emit(
                item.data(Qt.ItemDataRole.UserRole)
            )
        )
        layout.addWidget(self.list_widget, 1)

        self.empty_label = QLabel("Encara no hi ha alumnes.")
        self.empty_label.setObjectName("mutedText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

    def set_students(self, students) -> None:
        """Mostra alumnes i reutilitza files quan se'n conserva la identitat."""
        students = tuple(students)
        selected_id = self.current_student_id()
        current_ids = tuple(
            self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.list_widget.count())
        )
        incoming_ids = tuple(student.id for student in students)
        if current_ids == incoming_ids:
            for row, student in enumerate(students):
                item = self.list_widget.item(row)
                self.list_widget.itemWidget(item).update_student(student)
        else:
            self.list_widget.clear()
            for student in students:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, student.id)
                widget = StudentListItem(student)
                widget.note_requested.connect(self._request_note)
                size = widget.sizeHint()
                size.setHeight(max(size.height(), 52))
                item.setSizeHint(size)
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, widget)
                if student.id == selected_id:
                    self.list_widget.setCurrentItem(item)
        has_students = self.list_widget.count() > 0
        self.list_widget.setVisible(has_students)
        self.empty_label.setVisible(not has_students)
        self.batch_export_button.setEnabled(has_students)
        self.bulk_edit_button.setEnabled(has_students)
        self._update_selected_row()

    def current_student_id(self):
        """Retorna l'ID de l'alumne seleccionat, o `None` si no n'hi ha cap."""
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _emit_selection(self, current, previous=None) -> None:
        has_selection = current is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self._update_selected_row()
        if current is not None:
            self.student_selected.emit(current.data(Qt.ItemDataRole.UserRole))

    def _update_selected_row(self) -> None:
        current = self.list_widget.currentItem()
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            widget = self.list_widget.itemWidget(item)
            if widget is not None:
                widget.set_selected(item is current)

    def _request_note(self, student_id: int) -> None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == student_id:
                self.list_widget.setCurrentItem(item)
                break
        self.note_create_requested.emit(student_id)

    def _request_edit(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.edit_requested.emit(student_id)

    def _request_delete(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.delete_requested.emit(student_id)
