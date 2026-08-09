from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QTabWidget, QVBoxLayout, QWidget


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
        for name in self.TAB_NAMES:
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
        self.tabs.setTabText(0, student.full_name)

    def clear(self) -> None:
        self.tabs.hide()
        self.placeholder.show()
