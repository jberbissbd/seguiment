"""Controlador de la comprovació de versió nova en segon pla.

Llança la comprovació a l'arrencada sense bloquejar la interfície i, si
falla (sense connexió, GitHub no disponible, etc.), ho ignora en silenci:
mai mostra un error a l'usuari ni interromp l'inici de l'aplicació.
"""

import logging

from tutopy.ui.background_task import BackgroundTaskRunner
from tutopy.ui.dialogs.update_available_dialog import UpdateAvailableDialog
from tutopy.ui.main_window import MainWindow

LOGGER = logging.getLogger(__name__)


class UpdateController:
    """Comprova en segon pla si hi ha una versió nova i ho notifica si escau."""

    def __init__(self, window: MainWindow, update_check, preferences,
                 task_runner=None, dialog_factory=UpdateAvailableDialog):
        """Desa les dependències i sincronitza l'interruptor de preferències."""
        self.window = window
        self.update_check = update_check
        self.preferences = preferences
        self.task_runner = task_runner or BackgroundTaskRunner()
        self.dialog_factory = dialog_factory
        window.data_tools.update_check_toggled.connect(self._on_toggle_changed)
        window.data_tools.set_update_check_enabled(
            preferences.is_update_check_enabled()
        )

    def start(self) -> None:
        """Llança la comprovació en segon pla si la preferència ho permet."""
        if not self.preferences.is_update_check_enabled():
            return
        self.task_runner.start(
            lambda report_progress, is_cancelled: self.update_check.check_for_update(),
            on_success=self._on_result,
            on_failure=self._on_error,
        )

    def _on_result(self, result) -> None:
        if result.update_available and result.release_url:
            dialog = self.dialog_factory(
                result.latest_version, result.release_url, self.window
            )
            dialog.exec()

    def _on_error(self, error: Exception) -> None:
        LOGGER.info("Comprovació de versió fallida: %s", error)

    def _on_toggle_changed(self, enabled: bool) -> None:
        self.preferences.set_update_check_enabled(enabled)
