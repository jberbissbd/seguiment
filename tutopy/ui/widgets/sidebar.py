"""Barra lateral de navegació entre les seccions principals de l'aplicació."""

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QVBoxLayout

from tutopy.ui.resources import icon


class Sidebar(QFrame):
    """Navegació principal sense dependències de negoci."""

    section_changed = Signal(str)

    SECTIONS = (
        ("students", "Alumnes", "students.svg"),
        ("statistics", "Estadístiques", "statistics.svg"),
        ("configuration", "Configuració", "configuration.svg"),
        ("data", "Gestió de dades", "data.svg"),
    )

    def __init__(self, parent=None):
        """Construeix el botó de cada secció de `SECTIONS` i selecciona "Alumnes"."""
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(210)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(6)

        title = QLabel("Tutopy")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = {}
        for key, text, icon_name in self.SECTIONS:
            button = QPushButton(text)
            button.setIcon(icon(icon_name))
            button.setIconSize(QSize(19, 19))
            button.setCheckable(True)
            button.setProperty("navButton", True)
            button.setObjectName(f"nav_{key}")
            button.clicked.connect(
                lambda checked=False, section=key: self.section_changed.emit(section)
            )
            self.button_group.addButton(button)
            self.buttons[key] = button
            layout.addWidget(button)

        layout.addStretch()
        self.set_current_section("students")

    def set_current_section(self, section: str) -> None:
        """Marca com a seleccionat el botó corresponent a `section`, si existeix."""
        button = self.buttons.get(section)
        if button is not None:
            button.setChecked(True)
