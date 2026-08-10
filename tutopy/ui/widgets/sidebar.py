from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QVBoxLayout


class Sidebar(QFrame):
    """Navegació principal sense dependències de negoci."""

    section_changed = Signal(str)

    SECTIONS = (
        ("students", "Alumnes"),
        ("categories", "Categories"),
    )

    def __init__(self, parent=None):
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
        for key, text in self.SECTIONS:
            button = QPushButton(text)
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
        button = self.buttons.get(section)
        if button is not None:
            button.setChecked(True)
