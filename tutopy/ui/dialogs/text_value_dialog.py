"""Diàleg genèric per demanar un únic valor de text a l'usuari."""

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget,
)

from tutopy.ui.resources import set_dialog_button_icons


class TextValueDialog(QDialog):
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
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.value_input = QLineEdit(value)
        form.addRow(label, self.value_input)
        layout.addLayout(form)
        self.error_label = QLabel("El valor no pot estar buit.")
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

    def value(self):
        """Retorna el valor introduït sense espais sobrants."""
        return self.value_input.text().strip()

    def _accept_valid(self):
        if self.value():
            self.accept()
        else:
            self.error_label.show()
