from PySide6.QtWidgets import QLabel, QMainWindow

from tutopy.application import ServiceContainer


class MainWindow(QMainWindow):
    """Contenidor mínim sobre el qual es construirà la UI definitiva."""

    def __init__(self, services: ServiceContainer, parent=None):
        super().__init__(parent)
        self.services = services
        self.setWindowTitle("Tutopy — Seguiment d'alumnes")
        self.resize(1100, 700)
        self.setCentralWidget(QLabel("Interfície en preparació"))
