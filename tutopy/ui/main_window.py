"""Finestra principal de Tutopy: barra lateral, pàgines i diàlegs comuns.

Construeix l'esquelet de navegació de l'aplicació (alumnes, estadístiques,
configuració i gestió de dades) i ofereix punts d'entrada per mostrar
missatges d'estat, errors i confirmacions estàndard.
"""

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QSplitter,
    QStackedWidget, QVBoxLayout,
    QWidget, QMessageBox,
)

from tutopy.models.bulk_import import ImportIssue
from tutopy.ui.styles import MAIN_STYLESHEET
from tutopy.ui.widgets.sidebar import Sidebar
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.ui.widgets.student_list import StudentList
from tutopy.ui.widgets.crud_views import CrudListView
from tutopy.ui.widgets.data_tools import DataToolsView
from tutopy.ui.widgets.statistics_view import StatisticsView
from tutopy.ui.resources import application_icon


class MainWindow(QMainWindow):
    """Finestra principal: barra lateral de navegació i pila de pàgines."""

    def __init__(self, parent=None):
        """Construeix la barra lateral, les pàgines i mostra la d'alumnes."""
        super().__init__(parent)
        self.setWindowTitle("Tutopy — Seguiment d'alumnes")
        self.setWindowIcon(application_icon())
        self.resize(1100, 700)
        self.setMinimumSize(1180, 600)
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
        self.statistics_view = StatisticsView()
        self._pages = {
            "students": self._create_students_page(),
            "statistics": self._create_statistics_page(),
            "configuration": self._create_configuration_page(),
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

    def _create_statistics_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        heading = QLabel("Estadístiques de seguiment")
        heading.setObjectName("sectionTitle")
        description = QLabel(
            "Analitza la cobertura i l’evolució de les notes guardades. "
            "Els textos de les notes no es mostren ni s’analitzen."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(description)
        self.statistics_view.setMinimumHeight(720)
        scroll = QScrollArea()
        scroll.setObjectName("statisticsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.statistics_view)
        layout.addWidget(scroll, 1)
        self.statistics_scroll = scroll
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

    def _create_configuration_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(24, 24, 24, 24)
        heading = QLabel("Configuració")
        heading.setObjectName("sectionTitle")
        page_layout.addWidget(heading)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(18)

        category_panel = QFrame()
        category_panel.setObjectName("panel")
        category_layout = QVBoxLayout(category_panel)
        category_title = QLabel("Categories")
        category_title.setObjectName("studentName")
        category_description = QLabel(
            "Crea i edita les categories utilitzades per classificar les notes."
        )
        category_description.setObjectName("mutedText")
        category_description.setWordWrap(True)
        category_layout.addWidget(category_title)
        category_layout.addWidget(category_description)
        category_layout.addWidget(self.category_view)
        category_panel.setMinimumHeight(240)
        content_layout.addWidget(category_panel)
        content_layout.addWidget(self.data_tools.report_panel)

        scroll = QScrollArea()
        scroll.setObjectName("configurationScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)
        self.configuration_scroll = scroll
        return page

    def show_section(self, section: str) -> None:
        """Mostra la pàgina associada a `section` i marca el botó actiu.

        Args:
            section: Clau de la secció (`"students"`, `"statistics"`,
                `"configuration"` o `"data"`).
        """
        page = self._pages.get(section)
        if page is None:
            return
        self.content_stack.setCurrentWidget(page)
        self.sidebar.set_current_section(section)

    def show_status(self, message: str, timeout: int = 3000) -> None:
        """Mostra un missatge temporal a la barra d'estat.

        Args:
            message: Text a mostrar.
            timeout: Durada en mil·lisegons abans que el missatge desaparegui.
        """
        self.statusBar().showMessage(message, timeout)

    def show_error(self, message: str) -> None:
        """Mostra un diàleg d'error modal amb el missatge indicat."""
        QMessageBox.critical(self, "Error", message)

    def show_import_issues(self, issues: Sequence[ImportIssue]) -> None:
        """Mostra les files rebutjades d'una importació de full de càlcul.

        Args:
            issues: Col·lecció d'incidències (convertibles a text) a llistar.
        """
        QMessageBox.critical(
            self, "Errors al full de càlcul",
            "No s’ha importat cap dada. Revisa aquestes files:\n\n"
            + "\n".join(str(issue) for issue in issues),
        )

    def confirm_student_deletion(self, full_name: str) -> bool:
        """Demana confirmació abans d'eliminar un alumne i les seves dades.

        Returns:
            `True` si l'usuari confirma l'eliminació.
        """
        answer = QMessageBox.question(
            self,
            "Eliminar alumne",
            f"Vols eliminar {full_name} i totes les seves dades associades?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def confirm_note_deletion(self) -> bool:
        """Demana confirmació abans d'eliminar una nota de seguiment.

        Returns:
            `True` si l'usuari confirma l'eliminació.
        """
        answer = QMessageBox.question(
            self,
            "Eliminar nota",
            "Vols eliminar aquesta nota de seguiment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def confirm_deletion(self, entity_name: str) -> bool:
        """Demana confirmació genèrica abans d'eliminar `entity_name`.

        Returns:
            `True` si l'usuari confirma l'eliminació.
        """
        answer = QMessageBox.question(
            self, "Confirmar eliminació", f"Vols eliminar {entity_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes
