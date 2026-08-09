"""
Widget de filtres d'anotacions.

Permet filtrar anotacions per diferents criteris de manera combinada.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
)
from PySide6.QtCore import Signal, Slot, Qt, QDate
from PySide6.QtGui import QFont

from tutopy.models.messaging import Student, Category, AcademicCourse
from tutopy.controllers.student_controller import StudentController
from tutopy.services.category_service import CategoryService
from tutopy.services.academic_course_service import AcademicCourseService


class AnnotationFilterWidget(QWidget):
    """Widget per filtrar anotacions."""
    
    # Senyals
    filter_applied = Signal(dict)  # Emès amb els criteris de filtre
    filter_cleared = Signal()      # Emès quan es netegen els filtres
    
    def __init__(
        self,
        student_controller: StudentController,
        category_service: CategoryService,
        academic_course_service: AcademicCourseService,
        parent=None
    ):
        """
        Inicialitza el widget de filtres.
        
        Args:
            student_controller: Controlador d'alumnes
            category_service: Servei de categories
            academic_course_service: Servei de cursos acadèmics
            parent: Widget pare
        """
        super().__init__(parent)
        self.student_controller = student_controller
        self.category_service = category_service
        self.academic_course_service = academic_course_service
        
        # Carregar opcions de filtre
        self.students: list[Student] = []
        self.categories: list[Category] = []
        self.courses: list[AcademicCourse] = []
        
        self.setup_ui()
        self.load_filter_options()

    def setup_ui(self):
        """Configura la interfície del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Fila de filtres
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(10)
        
        # Filtre per tipus (categoria)
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("filter_combo")
        self.type_combo.setPlaceholderText("Tipus: totes")
        self.type_combo.setMinimumWidth(150)
        filter_layout.addWidget(QLabel("Tipus:"))
        filter_layout.addWidget(self.type_combo)
        
        # Filtre per contingut
        self.content_line = QLineEdit()
        self.content_line.setObjectName("filter_input")
        self.content_line.setPlaceholderText("Cerca en anotacions...")
        self.content_line.setMinimumWidth(200)
        filter_layout.addWidget(self.content_line)
        
        # Botons d'acció
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self.on_apply_clicked)
        filter_layout.addWidget(self.apply_button)
        
        self.clear_button = QPushButton("Netejar")
        self.clear_button.setObjectName("secondary")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        filter_layout.addWidget(self.clear_button)
        
        layout.addLayout(filter_layout)
        
        # Fila addicional amb més filtres (opcional, amagada per defecte)
        self.advanced_layout = QHBoxLayout()
        self.advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.advanced_layout.setSpacing(10)
        
        # Filtre per estudiant
        self.student_combo = QComboBox()
        self.student_combo.setObjectName("filter_combo")
        self.student_combo.setPlaceholderText("Tots els alumnes")
        self.student_combo.setMinimumWidth(150)
        self.advanced_layout.addWidget(QLabel("Alumne:"))
        self.advanced_layout.addWidget(self.student_combo)
        
        # Filtre per data (de)
        self.date_from = QDateEdit()
        self.date_from.setObjectName("filter_date")
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addYears(-1))  # Per defecte: fa 1 any
        self.advanced_layout.addWidget(QLabel("De:"))
        self.advanced_layout.addWidget(self.date_from)
        
        # Filtre per data (fins)
        self.date_to = QDateEdit()
        self.date_to.setObjectName("filter_date")
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.advanced_layout.addWidget(QLabel("Fins:"))
        self.advanced_layout.addWidget(self.date_to)
        
        # Filtre per curs acadèmic
        self.course_combo = QComboBox()
        self.course_combo.setObjectName("filter_combo")
        self.course_combo.setPlaceholderText("Tots els cursos")
        self.course_combo.setMinimumWidth(150)
        self.advanced_layout.addWidget(QLabel("Curs:"))
        self.advanced_layout.addWidget(self.course_combo)
        
        # Inicialment amagat
        self.advanced_layout.setVisible(False)
        layout.addLayout(self.advanced_layout)

    def load_filter_options(self):
        """Carrega les opcions per als filtres."""
        # Categories
        self.categories = self.category_service.get_all()
        self.type_combo.clear()
        self.type_combo.addItem("Totes", None)
        for category in self.categories:
            self.type_combo.addItem(category.name, category.id)
        
        # Cursos acadèmics
        self.courses = self.academic_course_service.get_all()
        self.course_combo.clear()
        self.course_combo.addItem("Tots els cursos", None)
        for course in self.courses:
            self.course_combo.addItem(course.course, course.id)
        
        # Alumnes
        self.students = self.student_controller.load_students()
        self.student_combo.clear()
        self.student_combo.addItem("Tots els alumnes", None)
        for student in self.students:
            self.student_combo.addItem(
                f"{student.name} {student.surnames} ({student.group_name})",
                student.id
            )

    def get_filters(self) -> dict:
        """
        Obté els criteris de filtre actuals.
        
        Returns:
            Diccionari amb els criteris de filtre
        """
        filters = {}
        
        # Tipus (categoria)
        category_id = self.type_combo.currentData()
        if category_id:
            filters['category_id'] = category_id
        
        # Contingut
        content = self.content_line.text().strip()
        if content:
            filters['content'] = content
        
        # Alumne
        student_id = self.student_combo.currentData()
        if student_id:
            filters['student_id'] = student_id
        
        # Data de
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        if date_from:
            filters['date_from'] = date_from
        
        # Data fins
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        if date_to:
            filters['date_to'] = date_to
        
        # Curs acadèmic
        course_id = self.course_combo.currentData()
        if course_id:
            filters['course_id'] = course_id
        
        return filters

    @Slot()
    def on_apply_clicked(self):
        """Es triggera quan es clica Aplicar."""
        filters = self.get_filters()
        self.filter_applied.emit(filters)

    @Slot()
    def on_clear_clicked(self):
        """Es triggera quan es clica Netejar."""
        self.content_line.clear()
        self.type_combo.setCurrentIndex(0)
        self.student_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addYears(-1))
        self.date_to.setDate(QDate.currentDate())
        
        self.filter_cleared.emit()

    def toggle_advanced(self, visible: bool):
        """
        Mostra o amaga els filtres avançats.
        
        Args:
            visible: Si True, mostra els filtres avançats
        """
        self.advanced_layout.setVisible(visible)
