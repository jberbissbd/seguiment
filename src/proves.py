import sys
from datetime import date

import PySide6.QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                               QFileDialog,
                               QFormLayout, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)


class Dialeg_Seleccio(QFileDialog):
    def __init__(self):
        super().__init__()

