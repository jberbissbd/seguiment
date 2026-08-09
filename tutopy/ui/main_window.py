"""
Finestra principal de l'aplicació Seguiment d'Alumnes.

Aquesta classe gestiona la finestra principal amb:
- Sidebar de navegació
- Llista d'alumnes
- Panell de detalls de l'alumne seleccionat
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon

from tutopy.ui.widgets.sidebar import Sidebar
from tutopy.ui.widgets.student_list import StudentListWidget
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.database.database import Database
from tutopy.services.student_service import StudentService
from tutopy.services.category_service import CategoryService
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.annotation_service import AnnotationService
from tutopy.services.validation_service import ValidationService
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.annotation_dao import AnnotationDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.controllers.student_controller import StudentController


class MainWindow(QMainWindow):
    """Finestra principal de l'aplicació."""
    
    # Senyals
    student_selected = Signal(int)  # Emès quan es selecciona un alumne
    
    def __init__(self, db_path: str):
        """
        Inicialitza la finestra principal.
        
        Args:
            db_path: Path de la base de dades
        """
        super().__init__()
        
        # Inicialitzar la base de dades i DAOs
        self.db = Database(db_path)
        self.init_daos()
        self.init_services()
        self.init_controllers()
        
        # Inicialitzar la UI
        self.setup_ui()
        self.connect_signals()

    def init_daos(self):
        """Inicialitza tots els DAOs."""
        self.student_dao = StudentDAO(self.db.conn)
        self.category_dao = CategoryDAO(self.db.conn)
        self.academic_course_dao = AcademicCourseDAO(self.db.conn)
        self.annotation_dao = AnnotationDAO(self.db.conn)
        self.contact_dao = ContactDAO(self.db.conn)
        self.document_dao = DocumentDAO(self.db.conn)
        self.group_history_dao = StudentGroupHistoryDAO(self.db.conn)

    def init_services(self):
        """Inicialitza tots els serveis."""
        self.validation_service = ValidationService(self.category_dao)
        self.category_service = CategoryService(self.category_dao, self.validation_service)
        self.academic_course_service = AcademicCourseService(self.academic_course_dao)
        self.annotation_service = AnnotationService(self.annotation_dao)
        self.student_service = StudentService(
            self.student_dao,
            self.contact_dao,
            self.document_dao,
            self.group_history_dao
        )

    def init_controllers(self):
        """Inicialitza tots els controladors."""
        self.student_controller = StudentController(
            self.student_service,
            self.category_service,
            self.academic_course_service
        )

    def setup_ui(self):
        """Configura la interfície d'usuari."""
        self.setMinimumSize(1024, 768)
        self.setWindowIcon(QIcon())  # TODO: Afegir icona
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horitzontal: sidebar + contingut)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (200px d'ample)
        self.sidebar = Sidebar(self)
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("sidebar")
        main_layout.addWidget(self.sidebar)
        
        # Contingut principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Barre de cerca
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search_input")
        self.search_bar.setPlaceholderText("Cerca alumne...")
        content_layout.addWidget(self.search_bar)
        
        # Àrea principal (llista + detalls)
        main_content = QWidget()
        main_content_layout = QHBoxLayout(main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(10)
        
        # Llista d'alumnes (250px d'ample)
        self.student_list = StudentListWidget(self.student_controller, self)
        self.student_list.setFixedWidth(250)
        main_content_layout.addWidget(self.student_list)
        
        # Panell de detalls (la resta de l'espai)
        self.student_detail_panel = StudentDetailPanel(
            self.student_controller,
            self.annotation_service,
            self.category_service,
            self.academic_course_service,
            self
        )
        main_content_layout.addWidget(self.student_detail_panel)
        
        content_layout.addWidget(main_content)

    def connect_signals(self):
        """Connecta els senyals entre components."""
        # Connectar selecció d'alumne
        self.student_list.student_selected.connect(self.on_student_selected)
        
        # Connectar cerca
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        
        # Connectar accions de la sidebar
        self.sidebar.new_student_requested.connect(self.on_new_student_requested)

    @Slot(int)
    def on_student_selected(self, student_id: int):
        """Es triggera quan es selecciona un alumne de la llista."""
        self.student_detail_panel.load_student(student_id)

    @Slot(str)
    def on_search_text_changed(self, text: str):
        """Es triggera quan el text de cerca canvia."""
        self.student_list.filter_students(text)

    @Slot()
    def on_new_student_requested(self):
        """Es triggera quan es sol·licita crear un nou alumne."""
        self.student_detail_panel.show_new_student_dialog()

    def closeEvent(self, event):
        """Es triggera quan es tanca la finestra."""
        # Tancar la connexió a la base de dades
        self.db.close()
        super().closeEvent(event)
