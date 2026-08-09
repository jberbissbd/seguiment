"""
Diàleg per crear o editar una anotació.

Mostra camps per a contingut, data, categoria i curs acadèmic.
"""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDateEdit,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from tutopy.models.messaging import (
    StudentAnnotation,
    StudentAnnotationNew,
    Category,
    AcademicCourse,
)


class AnnotationDialog(QDialog):
    """Diàleg per crear o editar una anotació."""
    
    def __init__(
        self,
        parent=None,
        annotation: StudentAnnotation = None,
        student_id: int = None,
        categories: list[Category] = None,
        courses: list[AcademicCourse] = None
    ):
        """
        Inicialitza el diàleg.
        
        Args:
            parent: Widget pare
            annotation: Anotació existent (per editar)
            student_id: ID de l'alumne associat
            categories: Llista de categories disponibles
            courses: Llista de cursos acadèmics disponibles
        """
        super().__init__(parent)
        self.annotation = annotation
        self.student_id = student_id
        self.categories = categories or []
        self.courses = courses or []
        
        self.setup_ui()
        
        # Si hi ha una anotació, omplir els camps
        if annotation:
            self.content_text.setPlainText(annotation.content)
            self.date_edit.setDate(QDate.fromString(annotation.date, "yyyy-MM-dd"))
            self.category_combo.setCurrentIndex(
                self.find_category_index(annotation.category_id)
            )
            self.course_combo.setCurrentIndex(
                self.find_course_index(annotation.course_id)
            )
        elif student_id:
            # Per defecte, posar data actual
            self.date_edit.setDate(QDate.currentDate())

    def setup_ui(self):
        """Configura la interfície del diàleg."""
        self.setWindowTitle(
            "Nova anotació" if not self.annotation else "Editar anotació"
        )
        self.setMinimumWidth(500)
        
        # Layout principal
        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Camp Contingut
        self.content_text = QTextEdit()
        self.content_text.setPlaceholderText("Introdueix el contingut de l'anotació...")
        self.content_text.setMinimumHeight(100)
        layout.addRow("Contingut:", self.content_text)
        
        # Camp Data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Data:", self.date_edit)
        
        # Camp Categoria
        self.category_combo = QComboBox()
        self.category_combo.setPlaceholderText("Selecciona una categoria")
        self.load_categories()
        layout.addRow("Categoria:", self.category_combo)
        
        # Camp Curs Acadèmic
        self.course_combo = QComboBox()
        self.course_combo.setPlaceholderText("Selecciona un curs (opcional)")
        self.load_courses()
        layout.addRow("Curs acadèmic:", self.course_combo)
        
        # Botons d'acció
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def load_categories(self):
        """Carrega les categories al combobox."""
        self.category_combo.clear()
        self.category_combo.addItem("Selecciona una categoria", None)
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)

    def load_courses(self):
        """Carrega els cursos acadèmics al combobox."""
        self.course_combo.clear()
        self.course_combo.addItem("Selecciona un curs (opcional)", None)
        for course in self.courses:
            self.course_combo.addItem(course.course, course.id)

    def find_category_index(self, category_id: int) -> int:
        """Troba l'índex d'una categoria pel seu ID."""
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == category_id:
                return i
        return 0

    def find_course_index(self, course_id: int) -> int:
        """Troba l'índex d'un curs pel seu ID."""
        for i in range(self.course_combo.count()):
            if self.course_combo.itemData(i) == course_id:
                return i
        return 0

    def accept(self):
        """Valida i guarda les dades."""
        # Validar camps obligatoris
        if not self.content_text.toPlainText().strip():
            # TODO: Mostrar error
            return
        
        super().accept()

    def get_annotation_data(self) -> StudentAnnotationNew:
        """
        Retorna les dades de l'anotació.
        
        Returns:
            Objecte StudentAnnotationNew amb les dades
        """
        content = self.content_text.toPlainText().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        category_id = self.category_combo.currentData() or 0
        course_id = self.course_combo.currentData() or 0
        
        return StudentAnnotationNew(
            student_id=self.student_id or 0,
            content=content,
            # NOTE: Les anotacions no tenen data ni curs a StudentAnnotationNew
            # Hem de revisar el model
        )

    def get_annotation_data_full(self) -> dict:
        """
        Retorna les dades completes de l'anotació (inclou data i curs).
        
        Returns:
            Diccionari amb totes les dades
        """
        return {
            'student_id': self.student_id or 0,
            'content': self.content_text.toPlainText().strip(),
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'category_id': self.category_combo.currentData() or 0,
            'course_id': self.course_combo.currentData() or 0,
        }
