"""Diàleg per crear o editar un contacte d'un alumne."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout

from tutopy.ui.resources import set_dialog_button_icons


class ContactDialog(QDialog):
    """Recull nom, relació, telèfon i correu d'un contacte, nou o existent."""

    def __init__(self, parent=None, contact=None):
        """Construeix el diàleg, precarregant les dades si s'edita un contacte existent.

        Args:
            parent: Widget pare de Qt, si escau.
            contact: Contacte existent a editar, o `None` per crear-ne un de nou.
        """
        super().__init__(parent)
        self.setWindowTitle("Editar contacte" if contact else "Nou contacte")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit(contact.name if contact else "")
        self.description_input = QLineEdit(contact.description if contact else "")
        self.phone_input = QLineEdit(contact.phone if contact else "")
        self.email_input = QLineEdit(contact.email if contact else "")
        form.addRow("Nom:", self.name_input)
        form.addRow("Relació:", self.description_input)
        form.addRow("Telèfon:", self.phone_input)
        form.addRow("Correu:", self.email_input)
        layout.addLayout(form)
        self.error_label = QLabel("El nom i la relació són obligatoris.")
        self.error_label.setObjectName("errorText")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        set_dialog_button_icons(self.buttons)
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def values(self):
        """Retorna les dades del contacte introduïdes, sense espais sobrants."""
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
        }

    def _accept_valid(self):
        values = self.values()
        if values["name"] and values["description"]:
            self.accept()
        else:
            self.error_label.show()
