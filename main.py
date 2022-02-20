import sys
from datetime import date

import main
from funcions import bbdd_conn, lectura_dades, demostracio_dades
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QGridLayout, QFormLayout, QDateEdit, \
    QApplication, QVBoxLayout, QTextEdit, QPushButton, QMainWindow, QMessageBox

# TODO: Registrar valors a la base de dades
# TODO: Afegir dades de trimestre
# TODO: Crear informe i exportar a Excel
# TODO: Moure funcions a arxiu funcions.


alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"

al_seguiment = ""
cat_seguiment = ""
al_registre: str = ""
cat_registre: str = ""
data_registre: str = date.isoformat(date.today())
t_registre: str = ""
n_caracters = 0


def arrencada():
    global al_seguiment
    global cat_seguiment
    dades = lectura_dades()
    al_seguiment = dades[0]
    cat_seguiment = dades[1]
    bbdd_conn()


def traspas_alumnes(text):
    """Captura el nom de l'alumne seleccionat com a variable de python"""
    global al_registre
    al_registre = text


def traspas_categoria(text):
    """Captura la categoria seleccionada com a variable de python"""
    global cat_registre
    cat_registre = text


def traspas_data(text):
    """Captura la data seleccionada i la transforma a python"""
    global data_registre
    data_python = text.toPython()
    data_registre = data_python


def registre_apretat():
    global al_registre
    global cat_registre
    global data_registre
    global t_registre
    demostracio_dades(al_registre, cat_registre, data_registre, t_registre)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        arrencada()
        global al_registre
        global cat_registre
        global data_registre
        self.setWindowTitle("Seguiment alumnes")
        self.setFixedSize(QSize(300, 200))
        # Configurem bloc d'alumnes:
        self.wcentral = QWidget()
        self.alumnes_etiqueta = QLabel("Alumne: ")
        self.setCentralWidget(self.wcentral)
        self.desplegable_al = QComboBox()
        self.desplegable_al.addItems(al_seguiment)
        al_registre = self.desplegable_al.currentText()
        self.desplegable_al.currentTextChanged.connect(traspas_alumnes)
        # Configurem bloc de motius:
        self.categories_etiqueta = QLabel("Motiu: ")
        self.desplegable_cat = QComboBox()
        self.desplegable_cat.addItems(cat_seguiment)
        cat_registre = self.desplegable_cat.currentText()
        self.desplegable_cat.currentTextChanged.connect(traspas_categoria)
        # Afegim data
        self.data_etiqueta = QLabel("Data:")
        self.selector_data = QDateEdit(date=date.today())
        self.selector_data.setDisplayFormat(u"dd/MM/yyyy")
        self.selector_data.setCalendarPopup(True)
        self.selector_data.dateChanged.connect(traspas_data)
        # Configurem disposició:
        self.disp_general = QVBoxLayout()
        # Configurem part formulari:
        self.form_dist = QFormLayout()
        self.form_dist.addRow(self.alumnes_etiqueta, self.desplegable_al)
        self.form_dist.addRow(self.categories_etiqueta, self.desplegable_cat)
        self.form_dist.addRow(self.data_etiqueta, self.selector_data)

        # Configurem text i botons:
        self.tbot = QGridLayout()
        self.qdesc_et = QLabel("Descripció:")
        self.qdesc = QTextEdit()
        self.regbot = QPushButton("Registrar")
        # self.regbot.clicked.connect(registre_apretat)
        self.regbot.clicked.connect(self.bot_prova)
        self.expbot = QPushButton("Exportar informe")
        self.bot_dist = QHBoxLayout()
        self.bot_dist.addWidget(self.regbot)
        self.bot_dist.addWidget(self.expbot)
        self.tbot.addWidget(self.qdesc_et, 0, 0)
        self.tbot.addWidget(self.qdesc, 0, 1)
        self.tbot.addLayout(self.bot_dist, 1, 0, 1, 2)
        # Configuració final de la part general:
        self.disp_general.addLayout(self.form_dist)
        self.disp_general.addLayout(self.tbot)
        self.wcentral.setLayout(self.disp_general)

    def bot_prova(self):
        global t_registre
        t_actual = self.qdesc.toPlainText()
        if t_actual == "":
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Registre buit")
            dlg.setText("No s'ha proporcionat cap descripció")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
        elif len(t_actual) > 350:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Text massa llarg")
            dlg.setText("La descripció introduïda excedeix els 350 caràcters")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
        else:
            t_registre = t_actual
            registre_apretat()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
