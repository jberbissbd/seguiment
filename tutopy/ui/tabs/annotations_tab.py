"""
Pestanya d'anotacions.

Mostra les anotacions d'un alumne i permet filtrar-les.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew
from tutopy.controllers.student_controller import StudentController
from tutopy.services.annotation_service import AnnotationService
from tutopy.services.category_service import CategoryService
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.ui.widgets.annotation_filter import AnnotationFilterWidget
from tutopy.ui.dialogs.annotation_dialog import AnnotationDialog


class AnnotationsTab(QWidget):
    """Pestanya que mostra les anotacions d'un alumne."""
    
    # Senyals
    annotation_created = Signal()
    annotation_updated = Signal()
    annotation_deleted = Signal()
    
    def __init__(
        self,
        student_controller: StudentController,
        annotation_service: AnnotationService,
        category_service: CategoryService,
        academic_course_service: AcademicCourseService,
        parent=None
    ):
        """
        Inicialitza la pestanya d'anotacions.
        
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
        
        self.current_student_id: int = None
        self.annotations: list[StudentAnnotation] = []
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Configura la interfície de la pestanya."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Filtres
        self.filter_widget = AnnotationFilterWidget(
            self.student_controller,
            self.category_service,
            self.academic_course_service,
            self
        )
        layout.addWidget(self.filter_widget)
        
        # Llista d'anotacions
        self.annotations_container = QWidget()
        self.annotations_layout = QVBoxLayout(self.annotations_container)
        self.annotations_layout.setContentsMargins(0, 0, 0, 0)
        self.annotations_layout.setSpacing(10)
        self.annotations_layout.setAlignment(Qt.AlignTop)
        
        # Missatge quan no hi ha anotacions
        self.no_annotations_label = QLabel("No hi ha anotacions per mostrar")
        self.no_annotations_label.setStyleSheet("color: #666;")
        self.no_annotations_label.setAlignment(Qt.AlignCenter)
        self.annotations_layout.addWidget(self.no_annotations_label)
        
        layout.addWidget(self.annotations_container)
        
        # Botó per afegir nova anotació
        self.new_button = QPushButton("+ Nova anotació")
        self.new_button.clicked.connect(self.on_new_clicked)
        layout.addWidget(self.new_button)

    def connect_signals(self):
        """Connecta els senyals."""
        self.filter_widget.filter_applied.connect(self.on_filter_applied)
        self.filter_widget.filter_cleared.connect(self.on_filter_cleared)

    def load_annotations(self, student_id: int):
        """
        Carrega les anotacions d'un alumne.
        
        Args:
            student_id: ID de l'alumne
        """
        self.current_student_id = student_id
        self.apply_filters({})  # sense filtres: totes les anotacions

    def apply_filters(self, filters: dict):
        """
        Aplica els filtres i mostra les anotacions corresponents.
        
        Args:
            filters: Diccionari amb els criteris de filtre
        """
        if not self.current_student_id:
            return
        
        # Si no hi ha filtre per estudiant, afegir el current_student_id
        if 'student_id' not in filters:
            filters = filters.copy()
            filters['student_id'] = self.current_student_id
        
        # Obtenir anotacions amb els filtres
        # TODO: Implementar mètode al servei per obtenir anotacions amb filtres
        # Per ara, obtenim totes les anotacions de l'alumne
        annotations = self.annotation_service.get_by_student(self.current_student_id)
        
        # Aplicar filtres localment (de moment)
        self.annotations = self.apply_local_filters(annotations, filters)
        
        # Mostrar les anotacions
        self.display_annotations()

    def apply_local_filters(
        self,
        annotations: list[StudentAnnotation],
        filters: dict
    ) -> list[StudentAnnotation]:
        """
        Aplica filtres localment a una llista d'anotacions.
        
        Args:
            annotations: Llista d'anotacions a filtrar
            filters: Diccionari amb criteris de filtre
            
        Returns:
            Llista d'anotacions filtrades
        """
        if not filters:
            return annotations
        
        result = []
        for ann in annotations:
            # Filtre per tipus (categoria)
            if 'category_id' in filters and ann.category_id != filters['category_id']:
                continue
            
            # Filtre per contingut
            if 'content' in filters:
                if filters['content'].lower() not in ann.content.lower():
                    continue
            
            # Filtre per data (de)
            if 'date_from' in filters and ann.date < filters['date_from']:
                continue
            
            # Filtre per data (fins)
            if 'date_to' in filters and ann.date > filters['date_to']:
                continue
            
            # Filtre per curs
            if 'course_id' in filters and ann.course_id != filters['course_id']:
                continue
            
            result.append(ann)
        
        return result

    def display_annotations(self):
        """Mostra les anotacions al widget."""
        # Netjar el layout
        while self.annotations_layout.count():
            item = self.annotations_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Si no hi ha anotacions, mostrar missatge
        if not self.annotations:
            self.annotations_layout.addWidget(self.no_annotations_label)
            return
        
        # Mostrar cada anotació
        for annotation in self.annotations:
            card = self.create_annotation_card(annotation)
            self.annotations_layout.addWidget(card)

    def create_annotation_card(self, annotation: StudentAnnotation) -> QWidget:
        """
        Crea una targeta per a una anotació.
        
        Args:
            annotation: L'anotació a mostrar
            
        Returns:
            Widget amb la targeta de l'anotació
        """
        from tutopy.ui.styles import (
            CATEGORY_ACADEMIC_COLOR, CATEGORY_ACADEMIC_TEXT,
            CATEGORY_FAMILY_COLOR, CATEGORY_FAMILY_TEXT,
            CATEGORY_BEHAVIOR_COLOR, CATEGORY_BEHAVIOR_TEXT
        )
        
        card = QWidget()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Capçalera: data + categoria
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Data
        date_label = QLabel(annotation.date)
        date_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(date_label)
        
        # Espai flexible
        header_layout.addStretch()
        
        # Categoria (tag amb color)
        category_name = self.get_category_name(annotation.category_id)
        category_color = self.get_category_color(annotation.category_id)
        category_label = QLabel(category_name)
        category_label.setStyleSheet(f"""
            background-color: {category_color['bg']};
            color: {category_color['text']};
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_layout.addWidget(category_label)
        
        layout.addLayout(header_layout)
        
        # Contingut
        content_label = QLabel(annotation.content)
        content_label.setStyleSheet("color: #333; font-size: 13px;")
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        # Accions (Editar, Eliminar)
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.addStretch()
        
        edit_button = QPushButton("Editar")
        edit_button.setObjectName("secondary")
        edit_button.clicked.connect(
            lambda: self.on_edit_clicked(annotation)
        )
        actions_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("danger")
        delete_button.clicked.connect(
            lambda: self.on_delete_clicked(annotation)
        )
        actions_layout.addWidget(delete_button)
        
        layout.addLayout(actions_layout)
        
        return card

    def get_category_name(self, category_id: int) -> str:
        """Obté el nom d'una categoria pel seu ID."""
        categories = self.category_service.get_all()
        for cat in categories:
            if cat.id == category_id:
                return cat.name
        return "Desconegut"

    def get_category_color(self, category_id: int) -> dict:
        """Obté el color d'una categoria pel seu ID."""
        from tutopy.ui.styles import (
            CATEGORY_ACADEMIC_COLOR, CATEGORY_ACADEMIC_TEXT,
            CATEGORY_FAMILY_COLOR, CATEGORY_FAMILY_TEXT,
            CATEGORY_BEHAVIOR_COLOR, CATEGORY_BEHAVIOR_TEXT
        )
        
        category_name = self.get_category_name(category_id).lower()
        
        colors = {
            'acadèmic': {'bg': CATEGORY_ACADEMIC_COLOR, 'text': CATEGORY_ACADEMIC_TEXT},
            'academic': {'bg': CATEGORY_ACADEMIC_COLOR, 'text': CATEGORY_ACADEMIC_TEXT},
            'família': {'bg': CATEGORY_FAMILY_COLOR, 'text': CATEGORY_FAMILY_TEXT},
            'family': {'bg': CATEGORY_FAMILY_COLOR, 'text': CATEGORY_FAMILY_TEXT},
            'conducta': {'bg': CATEGORY_BEHAVIOR_COLOR, 'text': CATEGORY_BEHAVIOR_TEXT},
            'behavior': {'bg': CATEGORY_BEHAVIOR_COLOR, 'text': CATEGORY_BEHAVIOR_TEXT},
        }
        
        return colors.get(category_name, {'bg': '#ccc', 'text': '#333'})

    @Slot()
    def on_new_clicked(self):
        """Es triggera quan es clica Nou."""
        if not self.current_student_id:
            return
        
        dialog = AnnotationDialog(
            self,
            student_id=self.current_student_id,
            categories=self.category_service.get_all()
        )
        if dialog.exec() == QDialog.Accepted:
            # TODO: Crear la nova anotació
            # annotation_data = dialog.get_annotation_data()
            # new_annotation = self.annotation_service.create(annotation_data)
            # self.annotation_created.emit()
            # self.load_annotations(self.current_student_id)
            pass

    @Slot(StudentAnnotation)
    def on_edit_clicked(self, annotation: StudentAnnotation):
        """Es triggera quan es clica Editar."""
        dialog = AnnotationDialog(
            self,
            annotation=annotation,
            categories=self.category_service.get_all()
        )
        if dialog.exec() == QDialog.Accepted:
            # TODO: Actualitzar l'anotació
            # updated_annotation = dialog.get_annotation_data()
            # self.annotation_service.update(updated_annotation)
            # self.annotation_updated.emit()
            # self.load_annotations(self.current_student_id)
            pass

    @Slot(StudentAnnotation)
    def on_delete_clicked(self, annotation: StudentAnnotation):
        """Es triggera quan es clica Eliminar."""
        from PySide6.QtWidgets import QMessageBox
        
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminació",
            f"Vols eliminar aquesta anotació?\n\n{annotation.content}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.annotation_service.delete(annotation.id)
            self.annotation_deleted.emit()
            self.load_annotations(self.current_student_id)

    @Slot(dict)
    def on_filter_applied(self, filters: dict):
        """Es triggera quan s'apliquen filtres."""
        self.apply_filters(filters)

    @Slot()
    def on_filter_cleared(self):
        """Es triggera quan es netegen els filtres."""
        if self.current_student_id:
            self.load_annotations(self.current_student_id)
