from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QPlainTextEdit, QVBoxLayout,
)

from tutopy.ui.widgets.date_input import DateInput


class NoteDialog(QDialog):
    """Recull una nota de seguiment sense accedir als serveis."""

    def __init__(self, parent=None, note=None, student_id=None, categories=()):
        super().__init__(parent)
        self.student_id = note.student_id if note else student_id
        self.setWindowTitle("Editar nota" if note else "Nova nota")
        self.setModal(True)
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.category_input = QComboBox()
        for category in categories:
            self.category_input.addItem(category.name, category.id)
        self.date_input = DateInput(QDate.currentDate())
        self.date_input.setToolTip(
            "Escriu la data en format DD/MM/AAAA o selecciona-la al calendari."
        )
        self.date_input.setAccessibleName("Data de la nota")
        self.date_input.setAccessibleDescription(
            "Data editable en format DD/MM/AAAA amb calendari emergent"
        )
        self.content_input = QPlainTextEdit()
        self.content_input.setPlaceholderText("Contingut de la nota de seguiment…")
        form.addRow("Categoria:", self.category_input)
        form.addRow("Data (DD/MM/AAAA):", self.date_input)
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

        if note:
            self._select_data(self.category_input, note.category_id)
            self.date_input.setDate(QDate.fromString(note.date, "yyyy-MM-dd"))
            self.content_input.setPlainText(note.content)

    def values(self) -> dict:
        return {
            "student_id": self.student_id,
            "category_id": self.category_input.currentData(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "course_id": 0,
            "content": self.content_input.toPlainText().strip(),
        }

    def _validate_and_accept(self) -> None:
        values = self.values()
        if values["student_id"] is None:
            self.validation_label.setText("No hi ha cap alumne seleccionat.")
        elif values["category_id"] is None:
            self.validation_label.setText("Cal seleccionar una categoria.")
        elif not self.date_input.date().isValid():
            self.validation_label.setText("La data ha de tenir el format DD/MM/AAAA.")
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
