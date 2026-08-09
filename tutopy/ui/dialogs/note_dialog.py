from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QPlainTextEdit, QVBoxLayout,
)


class NoteDialog(QDialog):
    """Recull una nota de seguiment sense accedir als serveis."""

    def __init__(self, parent=None, note=None, students=(), categories=(),
        courses=(), default_student_id=None):
        super().__init__(parent)
        self.setWindowTitle("Editar nota" if note else "Nova nota")
        self.setModal(True)
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.student_input = QComboBox()
        for student in students:
            label = (
                f"{student.full_name} · {student.group_name or 'Sense grup'} "
                f"· {student.uuid[:8]}"
            )
            self.student_input.addItem(label, student.id)
        self.category_input = QComboBox()
        for category in categories:
            self.category_input.addItem(category.name, category.id)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.course_input = QComboBox()
        self.course_input.addItem("Automàtic segons la data", 0)
        for course in courses:
            self.course_input.addItem(course.course, course.id)
        self.content_input = QPlainTextEdit()
        self.content_input.setPlaceholderText("Contingut de la nota de seguiment…")
        form.addRow("Alumne:", self.student_input)
        form.addRow("Categoria:", self.category_input)
        form.addRow("Data:", self.date_input)
        form.addRow("Curs acadèmic:", self.course_input)
        form.addRow("Contingut:", self.content_input)
        layout.addLayout(form)

        self.validation_label = QLabel()
        self.validation_label.setObjectName("errorText")
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText("Desar")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel·lar")
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        student_id = note.student_id if note else default_student_id
        self._select_data(self.student_input, student_id)
        if note:
            self._select_data(self.category_input, note.category_id)
            self._select_data(self.course_input, note.course_id)
            self.date_input.setDate(QDate.fromString(note.date, "yyyy-MM-dd"))
            self.content_input.setPlainText(note.content)

    def values(self) -> dict:
        return {
            "student_id": self.student_input.currentData(),
            "category_id": self.category_input.currentData(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "course_id": self.course_input.currentData(),
            "content": self.content_input.toPlainText().strip(),
        }

    def _validate_and_accept(self) -> None:
        values = self.values()
        if values["student_id"] is None:
            self.validation_label.setText("Cal seleccionar un alumne.")
        elif values["category_id"] is None:
            self.validation_label.setText("Cal seleccionar una categoria.")
        elif not values["content"]:
            self.validation_label.setText("El contingut no pot estar buit.")
        else:
            self.accept()
            return
        self.validation_label.show()

    @staticmethod
    def _select_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)
