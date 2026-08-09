"""
Panell de detalls de l'alumne.

Mostra la informació detallada d'un alumne seleccionat, incloent:
- Capçalera amb foto/inicials, nom, grup, edat, tutor
- Pestanyes per a anotacions, contactes, descriptors i documents
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QStackedWidget,
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont, QPixmap

from tutopy.models.messaging import Student, StudentNew
from tutopy.controllers.student_controller import StudentController
from tutopy.services.annotation_service import AnnotationService
from tutopy.services.category_service import CategoryService
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.ui.dialogs.student_dialog import StudentDialog
from tutopy.ui.tabs.annotations_tab import AnnotationsTab


class StudentDetailPanel(QWidget):
    """Panell que mostra els detalls d'un alumne."""
    
    # Senyals
    student_created = Signal()
    student_updated = Signal()
    
    def __init__(
        self,
        student_controller: StudentController,
        annotation_service: AnnotationService,
        category_service: CategoryService,
        academic_course_service: AcademicCourseService,
        parent=None
    ):
        """
        Inicialitza el panell de detalls.
        
        Args:
            student_controller: Controlador d'alumnes
            annotation_service: Servei d'anotacions
            category_service: Servei de categories
            academic_course_service: Servei de cursos acadèmics
            parent: Widget pare
        """
        super().__init__(parent)
        self.student_controller = student_controller
        self.annotation_service = annotation_service
        self.category_service = category_service
        self.academic_course_service = academic_course_service
        
        self.current_student: Student = None
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfície del panell."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Capçalera
        self.header_widget = self.create_header()
        layout.addWidget(self.header_widget)
        
        # Pestanyes de contingut
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("detail_tabs")
        
        # Pestanya d'Anotacions
        self.annotations_tab = AnnotationsTab(
            self.student_controller,
            self.annotation_service,
            self.category_service,
            self.academic_course_service,
            self
        )
        self.tab_widget.addTab(self.annotations_tab, "Anotacions")
        
        # Pestanya de Contactes (placeholder per ara)
        self.contacts_placeholder = QWidget()
        self.contacts_placeholder_layout = QVBoxLayout(self.contacts_placeholder)
        self.contacts_placeholder_layout.addWidget(QLabel("Contactes (properament)"))
        self.tab_widget.addTab(self.contacts_placeholder, "Contactes")
        
        # Pestanya de Descriptors (placeholder per ara)
        self.descriptors_placeholder = QWidget()
        self.descriptors_placeholder_layout = QVBoxLayout(self.descriptors_placeholder)
        self.descriptors_placeholder_layout.addWidget(QLabel("Descriptors (properament)"))
        self.tab_widget.addTab(self.descriptors_placeholder, "Descriptors")
        
        # Pestanya de Documents (placeholder per ara)
        self.documents_placeholder = QWidget()
        self.documents_placeholder_layout = QVBoxLayout(self.documents_placeholder)
        self.documents_placeholder_layout.addWidget(QLabel("Documents (properament)"))
        self.tab_widget.addTab(self.documents_placeholder, "Documents")
        
        layout.addWidget(self.tab_widget)

    def create_header(self) -> QWidget:
        """Crea el widget de la capçalera."""
        header = QWidget()
        header.setObjectName("card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(12)
        
        # Línia superior: avatar + info + botons
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Avatar (inicials en cercle)
        self.avatar_label = QLabel("LM")
        self.avatar_label.setStyleSheet("""
            background-color: #4F8EF7;
            color: white;
            border-radius: 30px;
            font-size: 24px;
            font-weight: bold;
            min-width: 60px;
            min-height: 60px;
            max-width: 60px;
            max-height: 60px;
        """)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.avatar_label)
        
        # Informació de l'alumne
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Nom
        self.name_label = QLabel("Nom Cognoms")
        self.name_label.setObjectName("title")
        info_layout.addWidget(self.name_label)
        
        # Detalls (grup, edat, tutor)
        self.details_label = QLabel("4t B • 15 anys • Tutor/a: J. Camps")
        self.details_label.setObjectName("subtitle")
        info_layout.addWidget(self.details_label)
        
        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        
        # Botons d'acció
        self.edit_button = QPushButton("Editar fitxa")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        top_layout.addWidget(self.edit_button)
        
        header_layout.addLayout(top_layout)
        
        return header

    def load_student(self, student_id: int):
        """
        Carrega les dades d'un alumne.
        
        Args:
            student_id: ID de l'alumne a cargar
        """
        student = self.student_controller.get_student(student_id)
        if student:
            self.current_student = student
            self.update_header()
            self.update_tabs()

    def update_header(self):
        """Actualitza la capçalera amb les dades de l'alumne actual."""
        if not self.current_student:
            return
        
        # Avatar: inicials
        initials = self.get_initials()
        self.avatar_label.setText(initials)
        
        # Nom
        self.name_label.setText(f"{self.current_student.name} {self.current_student.surnames}")
        
        # Detalls (de moment només grup, edat i tutor es calcularan més endavant)
        self.details_label.setText(f"{self.current_student.group_name}")

    def update_tabs(self):
        """Actualitza les pestanyes amb les dades de l'alumne actual."""
        if not self.current_student:
            return
        
        # Actualitzar pestanya d'anotacions
        self.annotations_tab.load_annotations(self.current_student.id)

    def get_initials(self) -> str:
        """Obté les inicials de l'alumne actual."""
        if not self.current_student:
            return "?"
        
        name_parts = self.current_student.name.split()
        surname_parts = self.current_student.surnames.split()
        
        first_initial = name_parts[0][0] if name_parts else ""
        second_initial = surname_parts[0][0] if surname_parts else ""
        
        return (first_initial + second_initial).upper()

    @Slot()
    def on_edit_clicked(self):
        """Es triggera quan es clica Editar fitxa."""
        self.show_edit_student_dialog()

    def show_new_student_dialog(self):
        """Mostra el diàleg per crear un nou alumne."""
        # Obtenir llista de grups
        groups = self.student_controller.get_all_groups()
        
        dialog = StudentDialog(self, groups=groups)
        if dialog.exec() == QDialog.Accepted:
            # Crear el nou alumne
            student_data = dialog.get_student_data()
            new_student = self.student_controller.create_student(student_data)
            
            # Recarregar la llista d'alumnes
            self.student_created.emit()
            
            # Seleccionar el nou alumne
            self.load_student(new_student.id)

    def show_edit_student_dialog(self):
        """Mostra el diàleg per editar l'alumne actual."""
        if not self.current_student:
            return
        
        # Obtenir llista de grups
        groups = self.student_controller.get_all_groups()
        
        dialog = StudentDialog(self, student=self.current_student, groups=groups)
        if dialog.exec() == QDialog.Accepted:
            # Actualitzar l'alumne
            student_data = dialog.get_student_data()
            # TODO: Implementar update al controlador
            # updated_student = self.student_controller.update_student(
            #     self.current_student.id, student_data
            # )
            
            # Recarregar les dades
            self.student_updated.emit()
            self.load_student(self.current_student.id)
