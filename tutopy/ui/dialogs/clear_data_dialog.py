from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout,
)

from tutopy.ui.resources import set_button_icon, set_dialog_button_icons


class ClearDataDialog(QDialog):
    CONFIRMATION = "ELIMINAR"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eliminar totes les dades")
        layout = QVBoxLayout(self)
        warning = QLabel(
            "Aquesta acció és irreversible i eliminarà totes les dades i els "
            "documents gestionats. Escriu ELIMINAR per continuar."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)
        self.confirmation_input = QLineEdit()
        self.confirmation_input.setPlaceholderText(self.CONFIRMATION)
        layout.addWidget(self.confirmation_input)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Eliminar definitivament")
        set_dialog_button_icons(self.buttons)
        set_button_icon(self.ok_button, "delete")
        self.ok_button.setEnabled(False)
        self.confirmation_input.textChanged.connect(
            lambda text: self.ok_button.setEnabled(text == self.CONFIRMATION)
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
