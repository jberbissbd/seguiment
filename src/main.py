import sys
from datetime import date

import PySide6.QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                               QFileDialog, QToolBar,
                               QFormLayout, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)

from funcions import (bbdd_conn, consulta_alumnes, export_global, export_escoltam,
                      lectura_dades, registre_dades)

# TODO: Reestructurar segons https://realpython.com/pyinstaller-python/


alumnat = 'src/dades/alumnat.csv'
categories = 'src/dades/categories.csv'

al_seguiment = ""
cat_seguiment = ""

t_registre: str = ""
n_caracters_total = 0

alumnes_registrats = []
al_seleccionat = ''


def arrencada():
    global al_seguiment
    global cat_seguiment
    dades = lectura_dades()
    al_seguiment = dades[0]
    cat_seguiment = dades[1]
    bbdd_conn()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.lim_caracters = 200
        arrencada()
        self.al_registre: str = ""
        self.cat_registre: str = ""
        global t_registre
        global n_caracters_total
        self.data_registre: str = date.isoformat(date.today())
        self.setWindowTitle("Seguiment alumnes")
        self.setFixedSize(PySide6.QtCore.QSize(300, 400))
        # Configurem barra d'eines:
        barra_eines = QToolBar("Hola")
        self.addToolBar(barra_eines)
        # Configurem bloc d'alumnes:
        self.wcentral = QWidget()
        self.alumnes_etiqueta = QLabel("Alumne: ")
        self.setCentralWidget(self.wcentral)
        self.desplegable_al = QComboBox()
        self.desplegable_al.addItems(al_seguiment)
        self.al_registre = self.desplegable_al.currentText()
        self.desplegable_al.currentTextChanged.connect(self.traspas_alumnes)
        # Configurem bloc de motius:
        self.categories_etiqueta = QLabel("Motiu: ")
        self.desplegable_cat = QComboBox()
        self.desplegable_cat.addItems(cat_seguiment)
        self.cat_registre = self.desplegable_cat.currentText()
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

        self.carrest_et = QLabel(str(self.lim_caracters - n_caracters_total) + " caràcters restants ")
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
        self.carrest_et.setText(str(self.lim_caracters - n_caracters_total) + " caràcters restants ")

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
        elif len(t_actual) > self.lim_caracters:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Text massa llarg")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText('La descripció introduïda excedeix els ' + str(self.lim_caracters) + ' caràcters')
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass
        else:
            t_registre = t_actual
            registre_dades(self.al_registre, self.cat_registre, self.data_registre, t_registre)
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
            self.alumnes_registrats = dades
            self.fin = FinestraExport()
            self.fin.show()

    def traspas_alumnes(self):
        """Captura el nom de l’alumne seleccionat com a variable de python"""
        self.al_registre = self.desplegable_al.currentText()

    def traspas_categoria(self):
        """Captura la categoria seleccionada cóm a variable de python"""
        self.cat_registre = self.desplegable_cat.currentText()

    def traspas_data(self):
        """Captura la data seleccionada i la transforma a python"""
        data_qt = self.selector_data.date()
        data_python = data_qt.toPython()
        self.data_registre = data_python


def executa(alumne):
    export_global(alumne)


class Dialeg_Seleccio(QFileDialog):
    def __init__(self):
        super().__init__()
        pass


class FinestraExport(QWidget):
    def __init__(self):
        super().__init__()
        self.al_seleccionat: str = ''
        self.carpeta_desti: str = ''
        self.arxiu_desti: str = ''
        self.alumnes_registrats = consulta_alumnes()
        # Creació dels elements de la finestra:
        self.disposicio = QGridLayout()
        self.disposicio.setColumnStretch(2, 2)
        self.setWindowTitle("Creació d'informe")
        self.resize(300, 100)
        self.alumne_etiqueta = QLabel("Alumne: ")
        self.alumne_seleccio = QComboBox()
        self.alumne_seleccio.addItems(self.alumnes_registrats)
        self.tots_etiqueta = QLabel("Exportar informes de\ntots els alumnes? ")
        self.tots_check = QCheckBox()
        self.tots_check.clicked.connect(self.tots_seleccionat)
        self.tots_check.setTristate(False)
        self.al_seleccionat = self.alumne_seleccio.currentText()
        self.alumne_seleccio.currentTextChanged.connect(self.canvi_alumne)
        self.desti = QLabel("Destí: ")
        self.desti_seleccio = QPushButton()
        self.desti_seleccio.setIcon(QIcon("icones/folder.png"))
        self.desti_seleccio.clicked.connect(self.seleccio_desti)
        self.boto_ok = QPushButton("D'acord")
        self.boto_ok.clicked.connect(export_escoltam)
        self.boto_cancela = QPushButton("Cancel·la")
        self.boto_cancela.clicked.connect(self.cancela)
        # Distribuïm els elements:
        self.setLayout(self.disposicio)
        self.disposicio.addWidget(self.alumne_etiqueta, 0, 0)
        self.disposicio.addWidget(self.alumne_seleccio, 0, 1)
        self.disposicio.addWidget(self.tots_etiqueta, 1, 0)
        self.disposicio.addWidget(self.tots_check)
        self.disposicio.addWidget(self.desti, 2, 0)
        self.disposicio.addWidget(self.desti_seleccio, 2, 1)
        self.disposicio.addWidget(self.boto_ok, 3, 0)
        self.disposicio.addWidget(self.boto_cancela, 3, 1)

    def seleccio_desti(self):
        # TODO: Obtenir retorn del directory seleccionat.
        # TODO: Dialeg s'executa dues vegades: deixar buit per a cancl·lar i directory seleccionat per a Ok.
        sel = QFileDialog()
        # sel.setFileMode(QFileDialog.AnyFile)
        # sel.setNameFilter("Excel (*.xlsx)")
        nom_arxiu = sel.getOpenFileName(self, "Open Image", "/home/jordi", "Image Files (*.png *.jpg *.bmp)")
        sel.exec()
        return nom_arxiu

    def cancela(self):
        self.close()

    def canvi_alumne(self):
        self.al_seleccionat = self.alumne_seleccio.currentText()

    def tots_seleccionat(self):
        if self.tots_check.isChecked():
            self.alumne_seleccio.setEnabled(False)
        else:
            self.alumne_seleccio.setEnabled(True)

    def informe_global(self):
        if self.tots_check.isChecked():
            for alumne in self.alumnes_registrats:
                export_global(alumne)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Informes exportats")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                dlg.close()
                self.close()
            else:
                pass

        elif self.tots_check.isChecked() is False:
            export_global(self.al_seleccionat)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Informes exportats")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                dlg.close()
                self.close()
            else:
                pass
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Sense dades")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No existeix cap alumne amb registres")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                pass
            else:
                pass


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
