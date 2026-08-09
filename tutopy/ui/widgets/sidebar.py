"""
Sidebar de navegació de l'aplicació.

Conté el menú principal amb les opcions de navegació i el botó
per crear nous alumnes.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from tutopy.ui.styles import PRIMARY_COLOR


class Sidebar(QWidget):
    """Sidebar de navegació."""
    
    # Senyals
    new_student_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Inicialitza el sidebar.
        
        Args:
            parent: Widget pare
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfície del sidebar."""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Títol
        self.title_label = QLabel("Seguiment\nd'Alumnes")
        self.title_label.setObjectName("sidebar_title")
        layout.addWidget(self.title_label)
        
        # Botons de navegació
        self.nav_buttons = {}
        
        # Botó Alumnes (seleccionat per defecte)
        self.btn_alumnes = QPushButton(" Alumnes")
        self.btn_alumnes.setObjectName("sidebar_button")
        self.btn_alumnes.setCheckable(True)
        self.btn_alumnes.setChecked(True)
        self.btn_alumnes.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        self.nav_buttons["alumnes"] = self.btn_alumnes
        layout.addWidget(self.btn_alumnes)
        
        # Botó Descriptors
        self.btn_descriptors = QPushButton(" Descriptors")
        self.btn_descriptors.setObjectName("sidebar_button")
        self.btn_descriptors.setCheckable(True)
        self.btn_descriptors.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        self.nav_buttons["descriptors"] = self.btn_descriptors
        layout.addWidget(self.btn_descriptors)
        
        # Botó Documents
        self.btn_documents = QPushButton(" Documents")
        self.btn_documents.setObjectName("sidebar_button")
        self.btn_documents.setCheckable(True)
        self.btn_documents.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        self.nav_buttons["documents"] = self.btn_documents
        layout.addWidget(self.btn_documents)
        
        # Botó Informes
        self.btn_informes = QPushButton(" Informes")
        self.btn_informes.setObjectName("sidebar_button")
        self.btn_informes.setCheckable(True)
        self.btn_informes.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        self.nav_buttons["informes"] = self.btn_informes
        layout.addWidget(self.btn_informes)
        
        # Botó Còpia de seguretat
        self.btn_copia = QPushButton(" Còpia de seguretat")
        self.btn_copia.setObjectName("sidebar_button")
        self.btn_copia.setCheckable(True)
        self.btn_copia.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        self.nav_buttons["copia"] = self.btn_copia
        layout.addWidget(self.btn_copia)
        
        # Separador
        layout.addStretch(1)
        
        # Botó Nou alumne
        self.btn_new_student = QPushButton(" + Nou alumne")
        self.btn_new_student.setObjectName("sidebar_button")
        self.btn_new_student.setStyleSheet(f"""
            QPushButton#sidebar_button {{
                background-color: {PRIMARY_COLOR};
                color: white;
                text-align: left;
                padding: 12px 16px;
                border-radius: 0px;
                border: none;
                font-size: 13px;
            }}
            QPushButton#sidebar_button:hover {{
                background-color: #3A7BEF;
            }}
        """)
        self.btn_new_student.clicked.connect(self.on_new_student_clicked)
        layout.addWidget(self.btn_new_student)
        
        # Versió
        self.version_label = QLabel("v0.0.1")
        self.version_label.setObjectName("sidebar_version")
        layout.addWidget(self.version_label)
        
        # Connectar botons de navegació
        for button in self.nav_buttons.values():
            button.clicked.connect(self.on_nav_button_clicked)

    def on_nav_button_clicked(self):
        """Es triggera quan es clica un botó de navegació."""
        button = self.sender()
        if button:
            # Desmarcar tots els botons
            for btn in self.nav_buttons.values():
                btn.setChecked(btn == button)

    def on_new_student_clicked(self):
        """Es triggera quan es clica el botó Nou alumne."""
        self.new_student_requested.emit()
