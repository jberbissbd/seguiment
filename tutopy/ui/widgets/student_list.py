from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout,
)


class StudentList(QFrame):
    """Llista visual d'alumnes; no consulta directament cap servei."""

    student_selected = Signal(int)
    search_changed = Signal(str)
    create_requested = Signal()

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
        header.addWidget(self.create_button)
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.search_changed)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.currentItemChanged.connect(self._emit_selection)
        layout.addWidget(self.list_widget, 1)

        self.empty_label = QLabel("Encara no hi ha alumnes.")
        self.empty_label.setObjectName("mutedText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

    def set_students(self, students) -> None:
        selected_id = self.current_student_id()
        self.list_widget.clear()
        for student in students:
            text = student.full_name
            if student.group_name:
                text = f"{text}\n{student.group_name}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            item.setToolTip(f"UUID: {student.uuid}")
            self.list_widget.addItem(item)
            if student.id == selected_id:
                self.list_widget.setCurrentItem(item)
        has_students = self.list_widget.count() > 0
        self.list_widget.setVisible(has_students)
        self.empty_label.setVisible(not has_students)

    def current_student_id(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _emit_selection(self, current, previous=None) -> None:
        if current is not None:
            self.student_selected.emit(current.data(Qt.ItemDataRole.UserRole))
