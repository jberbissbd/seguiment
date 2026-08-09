"""
Widget de llista d'alumnes.

Mostra una llista d'alumnes amb cerca i permet la selecció d'un alumne.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

from tutopy.models.messaging import Student
from tutopy.controllers.student_controller import StudentController
from .student_list_item import StudentListItem


class StudentListWidget(QWidget):
    """Widget que mostra una llista d'alumnes."""
    
    # Senyals
    student_selected = Signal(int)  # Emès amb l'ID de l'alumne seleccionat
    
    def __init__(self, controller: StudentController, parent=None):
        """
        Inicialitza el widget de llista d'alumnes.
        
        Args:
            controller: Controlador d'alumnes
            parent: Widget pare
        """
        super().__init__(parent)
        self.controller = controller
        self.students: list[Student] = []
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        """Configura la interfície del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Llista d'alumnes
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("student_list")
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

    def load_students(self):
        """Carrega tots els alumnes des del controlador."""
        self.students = self.controller.load_students()
        self.refresh_list()

    def refresh_list(self):
        """Actualitza la llista amb els alumnes actuals."""
        self.list_widget.clear()
        
        for student in self.students:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, student.id)
            item.setSizeHint(QSize(250, 70))  # Alçada fixa per als items
            
            # Crear el widget personalitzat per a l'alumne
            widget = StudentListItem(student)
            widget.setFixedWidth(230)  # Deixar marge
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def filter_students(self, query: str):
        """
        Filtra la llista d'alumnes segons una consulta de text.
        
        Args:
            query: Text de cerca
        """
        if not query:
            self.students = self.controller.load_students()
        else:
            self.students = self.controller.search_students(query)
        self.refresh_list()

    def select_student(self, student_id: int):
        """
        Selecciona un alumne per ID.
        
        Args:
            student_id: ID de l'alumne a seleccionar
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.data(Qt.UserRole) == student_id:
                self.list_widget.setCurrentItem(item)
                break

    @Slot(QListWidgetItem)
    def on_item_clicked(self, item: QListWidgetItem):
        """Es triggera quan es clica un element de la llista."""
        student_id = item.data(Qt.UserRole)
        if student_id is not None:
            self.student_selected.emit(student_id)

    @Slot(QListWidgetItem)
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Es triggera quan es fa doble clic a un element."""
        student_id = item.data(Qt.UserRole)
        if student_id is not None:
            self.student_selected.emit(student_id)

    def reload(self):
        """Recarrega la llista d'alumnes."""
        self.load_students()
