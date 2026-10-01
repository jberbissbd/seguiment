"""Diàleg que notifica que hi ha una versió nova de Tutopy disponible."""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from tutopy.ui.resources import set_button_icon, set_dialog_button_icons


class UpdateAvailableDialog(QDialog):
    """Informa que hi ha una versió nova i ofereix obrir la pàgina de descàrrega."""

    def __init__(self, latest_version: str, release_url: str, parent=None):
        """Construeix el diàleg amb la versió detectada i l'URL de la release."""
        super().__init__(parent)
        self.setWindowTitle("Versió nova disponible")
        self._release_url = release_url
        layout = QVBoxLayout(self)
        message = QLabel(f"Hi ha disponible la versió {latest_version} de Tutopy.")
        message.setWordWrap(True)
        layout.addWidget(message)
        note = QLabel(
            "La descàrrega es fa manualment des de la pàgina de GitHub."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        open_button = buttons.addButton(
            "Obrir pàgina de descàrrega", QDialogButtonBox.ButtonRole.ActionRole
        )
        set_button_icon(open_button, "open")
        open_button.clicked.connect(self._open_release_page)
        set_dialog_button_icons(buttons)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(
            self.accept
        )
        layout.addWidget(buttons)

    def _open_release_page(self) -> None:
        QDesktopServices.openUrl(QUrl(self._release_url))
