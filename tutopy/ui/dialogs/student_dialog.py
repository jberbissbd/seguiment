"""Diàleg per crear o editar les dades bàsiques d'un alumne."""

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QToolButton, QVBoxLayout,
)

from tutopy.ui.resources import set_button_icon, set_dialog_button_icons


class StudentDialog(QDialog):
    """Recull les dades necessàries per crear o editar un alumne."""

    def __init__(self, parent=None, student=None, groups=()):
        """Construeix el diàleg, precarregant les dades si s'edita un alumne existent.

        Args:
            parent: Widget pare de Qt, si escau.
            student: Alumne existent a editar, o `None` per crear-ne un de nou.
            groups: Noms de grup existents per emplenar el desplegable de grup.
        """
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
        self.group_selector_button = QToolButton()
        set_button_icon(self.group_selector_button, "dropdown")
        self.group_selector_button.setObjectName("selectorButton")
        self.group_selector_button.setToolTip("Mostrar els grups existents")
        self.group_selector_button.setAccessibleName("Seleccionar un grup existent")
        self.group_selector_button.clicked.connect(self.group_input.showPopup)
        group_layout = QHBoxLayout()
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(4)
        group_layout.addWidget(self.group_input, 1)
        group_layout.addWidget(self.group_selector_button)

        form.addRow("Nom:", self.name_input)
        form.addRow("Cognoms:", self.surnames_input)
        form.addRow("Grup:", group_layout)
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
        set_dialog_button_icons(self.buttons)
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        if student is not None:
            self.name_input.setText(student.name)
            self.surnames_input.setText(student.surnames)
            self.group_input.setCurrentText(student.group_name)

    def values(self) -> dict[str, str]:
        """Retorna les dades de l'alumne introduïdes, sense espais sobrants."""
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
