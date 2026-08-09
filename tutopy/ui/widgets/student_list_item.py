"""
Widget d'item de llista d'alumnes.

Mostra un alumne en format de targeta amb inicials, nom i grup.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from tutopy.models.messaging import Student


class StudentListItem(QWidget):
    """Widget que representa un alumne a la llista."""
    
    def __init__(self, student: Student):
        """
        Inicialitza l'item d'alumne.
        
        Args:
            student: Objecte Student amb les dades de l'alumne
        """
        super().__init__()
        self.student = student
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfície del widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Inicials en cercle
        initials_label = QLabel(self.get_initials())
        initials_label.setStyleSheet("""
            background-color: #4F8EF7;
            color: white;
            border-radius: 15px;
            padding: 5px;
            font-weight: bold;
            min-width: 30px;
            min-height: 30px;
            max-width: 30px;
            max-height: 30px;
            font-size: 14px;
        """)
        initials_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(initials_label)
        
        # Informació de l'alumne
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # Nom complet
        name_label = QLabel(f"{self.student.name} {self.student.surnames}")
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setStyleSheet("color: #333;")
        info_layout.addWidget(name_label)
        
        # Grup
        group_label = QLabel(self.student.group_name)
        group_label.setFont(QFont("Segoe UI", 8))
        group_label.setStyleSheet("color: #666;")
        info_layout.addWidget(group_label)
        
        layout.addLayout(info_layout)
        
        # Espai flexible per omplir
        layout.addStretch()

    def get_initials(self) -> str:
        """
        Obté les inicials de l'alumne.
        
        Returns:
            String amb les inicials (màxim 2 lletres)
        """
        name_parts = self.student.name.split()
        surname_parts = self.student.surnames.split()
        
        # Agafar la primera lletra del nom
        first_initial = name_parts[0][0] if name_parts else ""
        
        # Agafar la primera lletra del primer cognom
        second_initial = surname_parts[0][0] if surname_parts else ""
        
        return (first_initial + second_initial).upper()

    def sizeHint(self):
        """Retorna la mida recomanada per a l'item."""
        from PySide6.QtCore import QSize
        return QSize(250, 70)
