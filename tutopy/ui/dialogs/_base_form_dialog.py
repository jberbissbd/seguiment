"""Classe base per als diàlegs de formulari amb peu Desar/Cancel·lar.

La majoria de diàlegs de `tutopy/ui/dialogs` comparteixen el mateix peu:
una etiqueta d'error oculta (`error_label`) i un `QDialogButtonBox` amb
Desar/Cancel·lar que valida abans d'acceptar. `BaseFormDialog` centralitza
aquesta construcció perquè cada diàleg només s'hagi d'ocupar dels seus
propis camps.
"""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from tutopy.ui.resources import set_dialog_button_icons


class BaseFormDialog(QDialog):
    """Diàleg amb `self.layout`, etiqueta d'error i botons Desar/Cancel·lar.

    Les subclasses construeixen els seus propis camps a `self.layout` dins
    del seu `__init__` i acaben cridant `_add_footer(...)`. Per a
    validacions senzilles (un únic missatge fix) n'hi ha prou amb
    sobreescriure `_is_valid`; per a validacions amb missatges dinàmics, cal
    sobreescriure `_accept_valid`.
    """

    def __init__(self, parent: QWidget | None = None, title: str = ""):
        super().__init__(parent)
        if title:
            self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)

    def _add_footer(self, error_message: str = "", save_text: str = "Desar",
                     cancel_text: str = "Cancel·lar") -> None:
        """Afegeix l'etiqueta d'error i els botons Desar/Cancel·lar al final del diàleg."""
        self.error_label = QLabel(error_message)
        self.error_label.setObjectName("errorText")
        self.error_label.hide()
        self.layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        if save_text:
            self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(save_text)
        if cancel_text:
            self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(cancel_text)
        set_dialog_button_icons(self.buttons)
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def _is_valid(self) -> bool:
        """Retorna si el formulari és vàlid. Sobreescriure per a validació simple."""
        raise NotImplementedError

    def _accept_valid(self) -> None:
        """Valida el formulari i accepta el diàleg, o mostra l'error."""
        if self._is_valid():
            self.accept()
        else:
            self._show_error()

    def _show_error(self, message: str | None = None) -> None:
        """Mostra l'etiqueta d'error, opcionalment amb un missatge nou."""
        if message is not None:
            self.error_label.setText(message)
        self.error_label.show()
