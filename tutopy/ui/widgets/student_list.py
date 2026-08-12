from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget,
)

from tutopy.ui.widgets.avatar import avatar_stylesheet, initials


class StudentListItem(QWidget):
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(52)
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


class StudentList(QFrame):
    """Llista visual d'alumnes; no consulta directament cap servei."""

    student_selected = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)
    search_changed = Signal(str)
    create_requested = Signal()
    batch_export_requested = Signal()

    def __init__(self, parent=None):
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
        self.create_button.setObjectName("primaryButton")
        self.create_button.clicked.connect(self.create_requested)
        header.addWidget(title)
        header.addStretch()
        self.batch_export_button = QPushButton("Exportar diversos…")
        self.batch_export_button.setObjectName("secondaryButton")
        self.batch_export_button.setEnabled(False)
        self.batch_export_button.clicked.connect(self.batch_export_requested)
        header.addWidget(self.batch_export_button)
        header.addWidget(self.create_button)
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.search_changed)
        layout.addWidget(self.search_input)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
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
        selected_id = self.current_student_id()
        self.list_widget.clear()
        for student in students:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            widget = StudentListItem(student)
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

    def current_student_id(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _emit_selection(self, current, previous=None) -> None:
        has_selection = current is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        if current is not None:
            self.student_selected.emit(current.data(Qt.ItemDataRole.UserRole))

    def _request_edit(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.edit_requested.emit(student_id)

    def _request_delete(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.delete_requested.emit(student_id)
