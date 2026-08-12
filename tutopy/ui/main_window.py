from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QSplitter,
    QStackedWidget, QVBoxLayout,
    QWidget, QMessageBox,
)

from tutopy.ui.styles import MAIN_STYLESHEET
from tutopy.ui.widgets.sidebar import Sidebar
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.ui.widgets.student_list import StudentList
from tutopy.ui.widgets.crud_views import CrudListView
from tutopy.ui.widgets.data_tools import DataToolsView
from tutopy.ui.resources import application_icon


class MainWindow(QMainWindow):
    """Contenidor mínim sobre el qual es construirà la UI definitiva."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutopy — Seguiment d'alumnes")
        self.setWindowIcon(application_icon())
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
        self.category_view = CrudListView("Nova categoria")
        self.data_tools = DataToolsView()
        self._pages = {
            "students": self._create_students_page(),
            "categories": self._create_management_page("Categories", self.category_view),
            "data": self._create_management_page("Gestió de dades", self.data_tools),
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

    def _create_management_page(self, title: str, view: QWidget) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        if isinstance(view, DataToolsView):
            scroll = QScrollArea()
            scroll.setObjectName("dataToolsScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setWidget(view)
            layout.addWidget(scroll, 1)
            self.data_tools_scroll = scroll
        else:
            layout.addWidget(view, 1)
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

    def show_import_issues(self, issues) -> None:
        QMessageBox.critical(
            self, "Errors al full de càlcul",
            "No s’ha importat cap dada. Revisa aquestes files:\n\n"
            + "\n".join(str(issue) for issue in issues),
        )

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

    def confirm_deletion(self, entity_name: str) -> bool:
        answer = QMessageBox.question(
            self, "Confirmar eliminació", f"Vols eliminar {entity_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes
