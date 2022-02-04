from dinterficie.interficie_seguiment import main
import sys
from PySide6.QtWidgets import QApplication,QWidget,QMainWindow
from PySide6 import QtGui

if __name__ == '__main__':
    app = QApplication(sys.argv)
    programa = QMainWindow()
    programa = main.Ui_MainWindow()
    programa.setupUi(app)
    sys.exit(app.exec())