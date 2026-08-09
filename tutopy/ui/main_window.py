from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    """Contenidor mínim sobre el qual es construirà la UI definitiva."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutopy — Seguiment d'alumnes")
        self.resize(1100, 700)
        self.setCentralWidget(QLabel("Interfície en preparació"))
