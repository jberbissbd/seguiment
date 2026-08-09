from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit,
    QVBoxLayout,
)


class StudentDialog(QDialog):
    """Recull les dades necessàries per crear o editar un alumne."""

    def __init__(self, parent=None, student=None, groups=()):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle("Editar alumne" if student else "Nou alumne")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom")
        self.surnames_input = QLineEdit()
        self.surnames_input.setPlaceholderText("Cognoms")
        self.group_input = QComboBox()
        self.group_input.setEditable(True)
        self.group_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.group_input.addItems(groups)

        form.addRow("Nom:", self.name_input)
        form.addRow("Cognoms:", self.surnames_input)
        form.addRow("Grup:", self.group_input)
        layout.addLayout(form)

        self.validation_label = QLabel("El nom i els cognoms són obligatoris.")
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

        if student is not None:
            self.name_input.setText(student.name)
            self.surnames_input.setText(student.surnames)
            self.group_input.setCurrentText(student.group_name)

    def values(self) -> dict[str, str]:
        return {
            "name": self.name_input.text().strip(),
            "surnames": self.surnames_input.text().strip(),
            "group_name": self.group_input.currentText().strip(),
        }

    def _validate_and_accept(self) -> None:
        values = self.values()
        if not values["name"] or not values["surnames"]:
            self.validation_label.show()
            return
        self.accept()
