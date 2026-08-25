"""Controlador principal que coordina la navegació entre seccions de la barra lateral."""

from tutopy.ui.main_window import MainWindow


class MainController:
    """Coordina la navegació i la vista inicial d'alumnes."""

    def __init__(self, window: MainWindow):
        """Connecta el controlador amb la finestra principal i els seus senyals."""
        self.window = window
        self._connect_signals()

    def start(self) -> None:
        """Mostra la secció d'alumnes en obrir l'aplicació."""
        self.window.show_section("students")

    def _connect_signals(self) -> None:
        self.window.sidebar.section_changed.connect(self.change_section)

    def change_section(self, section: str) -> None:
        """Canvia la secció visible en resposta a la barra lateral.

        Args:
            section: Identificador de la secció a mostrar.
        """
        self.window.show_section(section)
