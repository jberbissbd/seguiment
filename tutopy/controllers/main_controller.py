from tutopy.ui.main_window import MainWindow


class MainController:
    """Coordina la navegació i la vista inicial d'alumnes."""

    def __init__(self, window: MainWindow):
        self.window = window
        self._connect_signals()

    def start(self) -> None:
        self.window.show_section("students")

    def _connect_signals(self) -> None:
        self.window.sidebar.section_changed.connect(self.change_section)

    def change_section(self, section: str) -> None:
        self.window.show_section(section)
