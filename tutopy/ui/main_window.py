from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QSplitter, QStackedWidget, QVBoxLayout,
    QWidget, QMessageBox,
)

from tutopy.ui.styles import MAIN_STYLESHEET
from tutopy.ui.widgets.sidebar import Sidebar
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.ui.widgets.student_list import StudentList


class MainWindow(QMainWindow):
    """Contenidor mínim sobre el qual es construirà la UI definitiva."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutopy — Seguiment d'alumnes")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MAIN_STYLESHEET)

        root = QWidget()
        root.setObjectName("applicationRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(18, 18, 18, 18)
        root_layout.addWidget(self.content_stack, 1)

        self.student_list = StudentList()
        self.student_detail = StudentDetailPanel()
        self._pages = {
            "students": self._create_students_page(),
            "categories": self._create_placeholder_page(
                "Categories", "La gestió de categories s'implementarà en una fase posterior."
            ),
            "courses": self._create_placeholder_page(
                "Cursos acadèmics", "La gestió de cursos s'implementarà en una fase posterior."
            ),
        }
        for page in self._pages.values():
            self.content_stack.addWidget(page)
        self.show_section("students")
        self.statusBar().showMessage("Preparat")

    def _create_students_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.student_list)
        splitter.addWidget(self.student_detail)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)
        splitter.setSizes([340, 720])
        layout.addWidget(splitter)
        return page

    def _create_placeholder_page(self, title: str, message: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        body = QLabel(message)
        body.setObjectName("mutedText")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        layout.addWidget(body, 1)
        return page

    def show_section(self, section: str) -> None:
        page = self._pages.get(section)
        if page is None:
            return
        self.content_stack.setCurrentWidget(page)
        self.sidebar.set_current_section(section)

    def show_status(self, message: str, timeout: int = 3000) -> None:
        self.statusBar().showMessage(message, timeout)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def confirm_student_deletion(self, full_name: str) -> bool:
        answer = QMessageBox.question(
            self,
            "Eliminar alumne",
            f"Vols eliminar {full_name} i totes les seves dades associades?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def confirm_note_deletion(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Eliminar nota",
            "Vols eliminar aquesta nota de seguiment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes
