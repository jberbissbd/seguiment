from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout, QFrame, QLabel, QTabWidget, QVBoxLayout, QWidget,
)


class StudentDetailPanel(QFrame):
    """Contenidor de les pestanyes de detall d'un alumne."""

    TAB_NAMES = (
        "Informació", "Notes", "Descriptors", "Contactes", "Documents", "Històric",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.placeholder = QLabel("Selecciona un alumne per consultar-ne el detall.")
        self.placeholder.setObjectName("mutedText")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder, 1)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.info_page = QWidget()
        info_layout = QFormLayout(self.info_page)
        self.name_value = QLabel()
        self.surnames_value = QLabel()
        self.group_value = QLabel()
        self.uuid_value = QLabel()
        self.uuid_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addRow("Nom:", self.name_value)
        info_layout.addRow("Cognoms:", self.surnames_value)
        info_layout.addRow("Grup:", self.group_value)
        info_layout.addRow("UUID:", self.uuid_value)
        self.tabs.addTab(self.info_page, "Informació")

        for name in self.TAB_NAMES[1:]:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            label = QLabel(f"{name}: contingut pendent d'implementar")
            label.setObjectName("mutedText")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_layout.addWidget(label)
            self.tabs.addTab(page, name)
        self.tabs.hide()
        layout.addWidget(self.tabs, 1)

    def show_student(self, student) -> None:
        if student is None:
            self.clear()
            return
        self.placeholder.hide()
        self.tabs.show()
        self.name_value.setText(student.name)
        self.surnames_value.setText(student.surnames)
        self.group_value.setText(student.group_name or "—")
        self.uuid_value.setText(student.uuid)

    def clear(self) -> None:
        self.tabs.hide()
        self.placeholder.show()
