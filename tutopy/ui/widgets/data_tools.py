from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class DataToolsView(QWidget):
    template_requested = Signal()
    import_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        import_panel = QFrame()
        import_panel.setObjectName("panel")
        import_layout = QVBoxLayout(import_panel)
        import_layout.addWidget(self._title("Importació massiva"))
        import_layout.addWidget(self._description(
            "Descarrega la plantilla, omple els fulls d’alumnes i categories i importa’ls en bloc."
        ))
        self.template_button = QPushButton("Descarregar plantilla XLSX")
        self.template_button.setObjectName("secondaryButton")
        self.import_button = QPushButton("Importar full de càlcul")
        self.import_button.setObjectName("primaryButton")
        import_layout.addWidget(self.template_button)
        import_layout.addWidget(self.import_button)

        danger_panel = QFrame()
        danger_panel.setObjectName("panel")
        danger_layout = QVBoxLayout(danger_panel)
        danger_layout.addWidget(self._title("Zona perillosa"))
        danger_layout.addWidget(self._description(
            "Elimina definitivament alumnes, notes, categories, contactes, descriptors, documents i cursos."
        ))
        self.clear_button = QPushButton("Eliminar totes les dades")
        self.clear_button.setObjectName("dangerButton")
        danger_layout.addWidget(self.clear_button)

        layout.addWidget(import_panel)
        layout.addWidget(danger_panel)
        layout.addStretch()
        self.template_button.clicked.connect(self.template_requested)
        self.import_button.clicked.connect(self.import_requested)
        self.clear_button.clicked.connect(self.clear_requested)

    @staticmethod
    def _title(text):
        label = QLabel(text)
        label.setObjectName("studentName")
        return label

    @staticmethod
    def _description(text):
        label = QLabel(text)
        label.setObjectName("mutedText")
        label.setWordWrap(True)
        return label
