from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from tutopy.models.messaging import Student, StudentNew


class StudentDialog(QDialog):
    """Diàleg per crear o editar un alumne.

    Mostra camps per a nom, cognoms i grup.
    El camp de grup permet escriure un valor nou o seleccionar-ne
    un d'existent entre els grups ja introduïts.
    Retorna les dades a través de les propietats ``name``,
    ``surnames`` i ``group_name``.
    """

    def __init__(self, parent=None, student: Student = None, groups: list[str] = None):
        super().__init__(parent)
        self.student = student
        self.groups = groups or []
        
        # Dades que es retornaran
        self.name: str = ""
        self.surnames: str = ""
        self.group_name: str = ""
        
        self.setup_ui()
        
        # Si hi ha un alumne, omplir els camps
        if student:
            self.name_line.setText(student.name)
            self.surnames_line.setText(student.surnames)
            self.group_combo.setEditText(student.group_name)

    def setup_ui(self):
        """Configura la interfície del diàleg."""
        self.setWindowTitle("Nou alumne" if not self.student else "Editar alumne")
        self.setMinimumWidth(400)
        
        # Layout principal
        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # Camp Nom
        self.name_line = QLineEdit()
        self.name_line.setPlaceholderText("Introdueix el nom")
        layout.addRow("Nom:", self.name_line)
        
        # Camp Cognoms
        self.surnames_line = QLineEdit()
        self.surnames_line.setPlaceholderText("Introdueix els cognoms")
        layout.addRow("Cognoms:", self.surnames_line)
        
        # Camp Grup
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)  # Permetre escriure grups nous
        self.group_combo.addItems(self.groups)
        self.group_combo.setPlaceholderText("Introdueix el grup")
        layout.addRow("Grup:", self.group_combo)
        
        # Botons d'acció
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def accept(self):
        """Guarda les dades i tanca el diàleg."""
        # Validar camps
        if not self.name_line.text().strip():
            # TODO: Mostrar missatge d'error
            return
        
        if not self.surnames_line.text().strip():
            # TODO: Mostrar missatge d'error
            return
            
        if not self.group_combo.currentText().strip():
            # TODO: Mostrar missatge d'error
            return
        
        # Guardar dades
        self.name = self.name_line.text().strip()
        self.surnames = self.surnames_line.text().strip()
        self.group_name = self.group_combo.currentText().strip()
        
        super().accept()

    def get_student_data(self) -> StudentNew:
        """Retorna les dades de l'alumne com a StudentNew."""
        return StudentNew(
            uuid="",  # Es generará al DAO
            name=self.name,
            surnames=self.surnames,
            group_name=self.group_name
        )