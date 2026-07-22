
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit

class StudentDialog(QDialog):
    """Diàleg per crear o editar un alumne.

    Mostra camps per a nom, cognoms i grup.
    El camp de grup permet escriure un valor nou o seleccionar-ne
    un d'existent entre els grups ja introduïts.
    Retorna les dades a través de les propietats ``name``,
    ``surnames`` i ``group_name``.
    """
    def __init__(self, parent=None, student=None, groups=None):
        super().__init__(parent)
        self.student = student
        self.name: str =""
        self.surnames: str =""
        self.group_name:str ""
        self.addRow("Nom",QLineEdit)