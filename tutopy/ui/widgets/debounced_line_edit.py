"""Controls de text que coalesceixen canvis consecutius de l'usuari."""

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLineEdit


class DebouncedLineEdit(QLineEdit):
    """Emet el text estable després d'un interval curt sense canvis.

    ``textChanged`` continua disponible per a comportaments purament visuals;
    les consultes o càlculs costosos s'han de connectar a ``debounced_text_changed``.
    """

    debounced_text_changed = Signal(str)

    def __init__(self, parent=None, delay_ms: int = 180):
        """Configura el temporitzador de debounce.

        Args:
            parent: Widget pare de Qt.
            delay_ms: Mil·lisegons d'inactivitat abans d'emetre
                `debounced_text_changed` (180 ms per defecte).
        """
        super().__init__(parent)
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(delay_ms)
        self._debounce_timer.timeout.connect(
            lambda: self.debounced_text_changed.emit(self.text())
        )
        self.textChanged.connect(self._debounce_timer.start)

    def cancel_pending(self) -> None:
        """Cancel·la una emissió pendent quan el consumidor refresca explícitament."""
        self._debounce_timer.stop()
