"""Diàleg per crear o editar un contacte d'un alumne."""

from PySide6.QtWidgets import QFormLayout, QLineEdit, QWidget

from tutopy.models.messaging import Contact
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog


class ContactDialog(BaseFormDialog):
    """Recull nom, relació, telèfon i correu d'un contacte, nou o existent."""

    def __init__(self, parent: QWidget | None = None, contact: Contact | None = None):
        """Construeix el diàleg, precarregant les dades si s'edita un contacte existent.

        Args:
            parent: Widget pare de Qt, si escau.
            contact: Contacte existent a editar, o `None` per crear-ne un de nou.
        """
        super().__init__(parent, "Editar contacte" if contact else "Nou contacte")
        form = QFormLayout()
        self.name_input = QLineEdit(contact.name if contact else "")
        self.description_input = QLineEdit(contact.description if contact else "")
        self.phone_input = QLineEdit(contact.phone if contact else "")
        self.email_input = QLineEdit(contact.email if contact else "")
        form.addRow("Nom:", self.name_input)
        form.addRow("Relació:", self.description_input)
        form.addRow("Telèfon:", self.phone_input)
        form.addRow("Correu:", self.email_input)
        self.layout.addLayout(form)
        self._add_footer("El nom i la relació són obligatoris.")

    def values(self):
        """Retorna les dades del contacte introduïdes, sense espais sobrants."""
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
        }

    def _is_valid(self):
        values = self.values()
        return bool(values["name"] and values["description"])
