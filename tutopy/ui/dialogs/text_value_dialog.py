"""Diàleg genèric per demanar un únic valor de text a l'usuari."""

from PySide6.QtWidgets import QFormLayout, QLineEdit, QWidget

from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog


class TextValueDialog(BaseFormDialog):
    """Recull un valor de text obligatori, amb títol i etiqueta configurables."""

    def __init__(
        self, title: str, label: str, value: str = "", parent: QWidget | None = None
    ):
        """Construeix el diàleg amb el títol i l'etiqueta indicats.

        Args:
            title: Títol de la finestra del diàleg.
            label: Text de l'etiqueta que acompanya el camp de text.
            value: Valor inicial del camp de text.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent, title)
        form = QFormLayout()
        self.value_input = QLineEdit(value)
        form.addRow(label, self.value_input)
        self.layout.addLayout(form)
        self._add_footer("El valor no pot estar buit.")

    def value(self):
        """Retorna el valor introduït sense espais sobrants."""
        return self.value_input.text().strip()

    def _is_valid(self):
        return bool(self.value())
