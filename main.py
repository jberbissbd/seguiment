import sys
from datetime import date

import PySide6.QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QGridLayout, QFormLayout, QDateEdit, \
    QApplication, QVBoxLayout, QTextEdit, QPushButton, QMainWindow, QMessageBox

from funcions import bbdd_conn, lectura_dades, registre_dades, consulta_alumnes, consulta_dades, pandes_prova

# TODO: Afegir dades de trimestre
# TODO: Crear informe i exportar a Excel


alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"

al_seguiment = ""
cat_seguiment = ""
al_registre: str = ""
cat_registre: str = ""
data_registre: str = date.isoformat(date.today())
t_registre: str = ""
n_caracters_total = 0
lim_caracters = 200
alumnes_registrats = []
al_seleccionat = ''


def arrencada():
    global al_seguiment
    global cat_seguiment
    dades = lectura_dades()
    al_seguiment = dades[0]
    cat_seguiment = dades[1]
    bbdd_conn()


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        arrencada()
        global al_registre
        global cat_registre
        global data_registre
        global t_registre
        global n_caracters_total
        global lim_caracters
        self.setWindowTitle("Seguiment alumnes")
        self.setFixedSize(PySide6.QtCore.QSize(300, 400))
        # Configurem bloc d'alumnes:
        self.wcentral = QWidget()
        self.alumnes_etiqueta = QLabel("Alumne: ")
        self.setCentralWidget(self.wcentral)
        self.desplegable_al = QComboBox()
        self.desplegable_al.addItems(al_seguiment)
        al_registre = self.desplegable_al.currentText()
        self.desplegable_al.currentTextChanged.connect(self.traspas_alumnes)
        # Configurem bloc de motius:
        self.categories_etiqueta = QLabel("Motiu: ")
        self.desplegable_cat = QComboBox()
        self.desplegable_cat.addItems(cat_seguiment)
        cat_registre = self.desplegable_cat.currentText()
        self.desplegable_cat.currentTextChanged.connect(self.traspas_categoria)
        # Configurem bloc de descripció:
        self.qdesc_et = QLabel("Descripció:")
        self.qdesc_et.setFixedSize(100, 30)
        self.qdesc = QTextEdit()
        self.qdesc.textChanged.connect(self.limit_caracters)
        # Afegim data
        self.data_etiqueta = QLabel("Data:")
        avui = PySide6.QtCore.QDate.currentDate()
        self.selector_data = QDateEdit(avui)
        self.selector_data.setDisplayFormat(u"dd/MM/yyyy")
        self.selector_data.setCalendarPopup(True)
        self.selector_data.dateChanged.connect(self.traspas_data)

        # Configurem disposició:
        self.disp_general = QVBoxLayout()
        # Configurem part formulari:
        self.form_dist = QFormLayout()
        self.form_dist.setVerticalSpacing(0)
        self.form_dist.setHorizontalSpacing(0)
        self.form_dist.setContentsMargins(1, 1, 1, 1)

        self.form_dist.addRow(self.alumnes_etiqueta, self.desplegable_al)
        self.form_dist.addRow(self.categories_etiqueta, self.desplegable_cat)
        self.form_dist.addRow(self.data_etiqueta, self.selector_data)
        self.form_dist.addRow(self.qdesc_et, self.qdesc)

        # Configurem text i botons:
        self.tbot = QGridLayout()

        self.carrest_et = QLabel(str(lim_caracters - n_caracters_total) + " caràcters restants ")
        self.regbot = QPushButton("Registrar")
        self.regbot.clicked.connect(self.boto_registre)
        self.expbot = QPushButton("Exportar informe")
        self.expbot.clicked.connect(self.boto_exportar)
        self.bot_dist = QHBoxLayout()
        self.bot_dist.addWidget(self.regbot)
        self.bot_dist.addWidget(self.expbot)
        self.tbot.addWidget(self.carrest_et, 0, 0)
        self.tbot.addLayout(self.bot_dist, 1, 0, 1, 2)
        # Configuració final de la part general:
        self.disp_general.addLayout(self.form_dist)
        self.disp_general.addLayout(self.tbot)
        self.wcentral.setLayout(self.disp_general)

    def limit_caracters(self):
        global n_caracters_total
        text_escrit = self.qdesc.toPlainText()
        n_caracters_total = len(text_escrit)
        self.carrest_et.setText(str(lim_caracters - n_caracters_total) + " caràcters restants ")

    def boto_registre(self):
        global t_registre
        t_actual = self.qdesc.toPlainText()
        if t_actual == "":
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Registre buit")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No s'ha proporcionat cap descripció")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass
        elif len(t_actual) > lim_caracters:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Text massa llarg")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText('La descripció introduïda excedeix els ' + str(lim_caracters) + ' caràcters')
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass
        else:
            t_registre = t_actual
            registre_dades(al_registre, cat_registre, data_registre, t_registre)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Registre introduït")
            boto = dlg.exec()
            self.qdesc.clear()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass

    def boto_exportar(self):
        global alumnes_registrats
        dades = consulta_alumnes()
        if not dades:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Sense dades")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No existeix cap alumne amb registres")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass
        else:
            alumnes_registrats = dades
            self.fin = FinestraExport()
            self.fin.show()

    def traspas_alumnes(self):
        """Captura el nom de l'alumne seleccionat com a variable de python"""
        global al_registre
        al_registre = self.desplegable_al.currentText()

    def traspas_categoria(self):
        """Captura la categoria seleccionada com a variable de python"""
        global cat_registre
        cat_registre = self.desplegable_cat.currentText()

    def traspas_data(self):
        """Captura la data seleccionada i la transforma a python"""
        global data_registre
        data_qt = self.selector_data.date()
        data_python = data_qt.toPython()
        data_registre = data_python


def executa():
    global al_seleccionat

    # for fila in a:
    #     print(fila)
    pandes_prova(al_seleccionat)


class FinestraExport(QWidget):
    def __init__(self):
        super().__init__()
        global al_seleccionat
        # Creació dels elements de la finestra:
        self.disposicio = QGridLayout()
        self.disposicio.setColumnStretch(2, 2)
        self.setWindowTitle("Creació d'informe")
        self.resize(300, 100)
        self.alumne_etiqueta = QLabel("Alumne: ")
        self.alumne_seleccio = QComboBox()
        self.alumne_seleccio.addItems(alumnes_registrats)
        al_seleccionat = self.alumne_seleccio.currentText()
        self.alumne_seleccio.currentTextChanged.connect(self.canvi_alumne)
        self.desti = QLabel("Destí: ")
        self.desti_seleccio = QPushButton()
        self.desti_seleccio.setIcon(QIcon("icones/folder.png"))
        self.boto_ok = QPushButton("D'acord")
        self.boto_ok.clicked.connect(executa)
        self.boto_cancela = QPushButton("Cancel·la")
        self.boto_cancela.clicked.connect(self.cancela)
        # Distribuïm els elements:
        self.setLayout(self.disposicio)
        self.disposicio.addWidget(self.alumne_etiqueta, 0, 0)
        self.disposicio.addWidget(self.alumne_seleccio, 0, 1)
        self.disposicio.addWidget(self.desti, 1, 0)
        self.disposicio.addWidget(self.desti_seleccio, 1, 1)
        self.disposicio.addWidget(self.boto_ok, 2, 0)
        self.disposicio.addWidget(self.boto_cancela, 2, 1)

    def cancela(self):
        self.close()

    def canvi_alumne(self):
        global al_seleccionat
        al_seleccionat = self.alumne_seleccio.currentText()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
