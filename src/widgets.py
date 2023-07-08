import datetime
import os
from typing import Union

import dateutil
import pyexcel_io
import pyexcel_xls
import pyexcel_xlsxr
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QDate, QSize, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QDateEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QAbstractItemView,
    QDialog,
    QMessageBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QFileDialog, QGroupBox, QButtonGroup, QRadioButton, QTableWidget, QTableWidgetItem,
    QItemDelegate, QStyledItemDelegate
)
from dateutil.parser import parser

from agents_bbdd import AjudantDirectoris
from agents_gui import Calendaritzador, CapEstudis, ExportadorImportador, CreadorInformes, Comptable, Classificador
from formats import Alumne_comm, AlumneNou, DataGuiComm, DataNova, Registresguicomm, Registres_gui_nou

QLocale.setDefault(QLocale.Catalan)


def obtenir_llistat_alumnes():
    CapEstudis(1).refrescar_alumnes()
    alumnes_entrada = CapEstudis(1).alumnat
    if alumnes_entrada:
        llistat_alumnes = [alumne.nom.strip() for alumne in alumnes_entrada]
        return llistat_alumnes
    return False


def obtenir_registres_alumnes():
    alumnes_entrada = CapEstudis(1).alumnat
    if alumnes_entrada:
        llistat_dades_alumnes = [[alumne.id, alumne.nom] for alumne in alumnes_entrada]
        return llistat_dades_alumnes
    return False


def obtenir_categories():
    categories_entrada = Classificador(1).categories
    if categories_entrada:
        llistat_categories = [categoria.nom for categoria in categories_entrada]
        return llistat_categories
    return []


def obtenir_llistat_registres():
    Comptable(1).refrescar_registres()
    if Comptable(1).registres:
        llista_registres = [[element.id, element.alumne.nom, element.categoria.nom,
                             dateutil.parser.parse(element.data).date(), element.descripcio] for element
                            in Comptable(1).registres]
        return llista_registres
    return None


def obtenir_llistat_categories_registrades():
    categories_registre = Classificador(1).obtenir_categories_registrades()
    if categories_registre:
        llistat_alumnes = [categoria.nom for categoria in categories_registre]
        return llistat_alumnes
    return False


def obtenir_llistat_alumnes_registrats():
    alumnes_entrada = CapEstudis(1).alumnat_registres
    if alumnes_entrada:
        llistat_alumnes = [alumne.nom for alumne in alumnes_entrada]
        return llistat_alumnes
    return False


class DelegatDates(QStyledItemDelegate):
    """Delegat per a la columna de dates"""

    def __init__(self, parent):
        super(DelegatDates, self).__init__()
        self.editor = None

    def displayText(self, value, locale) -> str:
        """Retorna el text que es mostra a la columna de dates"""
        if value != str(""):
            value = value.toPython()
        return value.strftime("%d/%m/%Y")

    def createEditor(self, parent, option, index):
        self.editor = QDateEdit(parent)
        valor_actual = index.data()
        self.editor.setDate(valor_actual)
        self.editor.setCalendarPopup(True)
        self.editor.setDisplayFormat("dd/MM/yyyy")
        return self.editor


class DelegatAlumnes(QItemDelegate):
    """
    A delegate to add QComboBox in every cell of the given column
    """

    def __init__(self, parent):
        super(DelegatAlumnes, self).__init__(parent)
        self.combobox = None
        self.llista_valors = None
        self.parent = parent

    def createEditor(self, parent, option, index):
        self.combobox = QComboBox(parent)
        self.llista_valors = obtenir_llistat_alumnes()
        self.combobox.addItems(self.llista_valors)
        valor_actual = index.data()
        posicio_valor_actual = self.llista_valors.index(valor_actual)
        self.combobox.setCurrentIndex(posicio_valor_actual)
        return self.combobox

    def setEditorData(self, editor, index):
        value = index.data()
        return value


class DelegatCategories(QItemDelegate):
    """
    A delegate to add QComboBox in every cell of the given column
    """

    def __init__(self, parent):
        super(DelegatCategories, self).__init__(parent)
        self.combobox = None
        self.llista_valors = None
        self.parent = parent

    def createEditor(self, parent, option, index):
        self.combobox = QComboBox(parent)
        self.llista_valors = obtenir_categories()
        self.combobox.addItems(self.llista_valors)
        valor_actual = index.data()
        posicio_valor_actual = self.llista_valors.index(valor_actual)
        self.combobox.setCurrentIndex(posicio_valor_actual)
        return self.combobox

    def setEditorData(self, editor, index):
        value = index.data()
        return value


class DialegSeleccioCarpeta(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.Directory)
        self.setWindowTitle("Selecciona una carpeta")


class DialegAfegir(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.buttonsBox = None
        self.nomcomplet = None
        self.setWindowTitle("Afegir alumne")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None
        self.setupUI()

    def setupUI(self):
        self.nomcomplet = QLineEdit()
        self.nomcomplet.setObjectName("Nom complet")
        disposicio = QFormLayout()
        disposicio.addRow("Nom:", self.nomcomplet)
        self.layout.addLayout(disposicio)
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = []
        if not self.nomcomplet.text():
            QMessageBox.critical(
                self,
                "Error!",
                f"Ha de proporcionar un {self.nomcomplet.objectName()}",
            )
            self.data = None  # Reset .data
            return
        self.data.append(["", self.nomcomplet.text()])
        if not self.data:
            return
        super().accept()


class DialegEliminar(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("ATENCIO")
        self.setText(
            "Aquesta acció tambe esborrarà els\nregistres de l'alumne seleccionat. Estàs segur?"
        )
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setButtonText(QMessageBox.Yes, "Si, esborrar")
        self.setIcon(QMessageBox.Warning)


class DialegInformacio(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("LLicencies")
        self.text_mostrar = "Tutopy: <a href='https://github.com/jberbissbd/seguiment'>repositori</a>\nIcones: " \
                            "Papirus <a href='https://github.com/PapirusDevelopmentTeam/papirus-icon-theme" \
                            "/'>repositori</a> \nLLicencia: GPL-3.0<a " \
                            "href='https://www.gnu.org/licenses/gpl-3.0.ca.html'> GPL-3.0</a>"
        self.setText(self.text_mostrar)
        self.setStandardButtons(QMessageBox.Yes)
        self.setButtonText(QMessageBox.Yes, "D'acord")
        self.setIcon(QMessageBox.Information)


class EditorDates(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.calendari_editor_dates = Calendaritzador(1)
        self.AMPLADA_ETIQUETES = 75
        self.AMPLADA_DESPLEGABLES = 200
        self.setWindowTitle("Editor_Dates")
        self.setGeometry(300, 300, 300, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        DISTRIBUCIO.setHorizontalSpacing(10)
        self.setLayout(DISTRIBUCIO)
        # Definim els editors de dates:
        self.DATA_SEGON_TRIMESTRE = QDateEdit()
        self.DATA_SEGON_TRIMESTRE.setDisplayFormat("dd/MM/yyyy")
        self.DATA_SEGON_TRIMESTRE.setCalendarPopup(True)
        self.DATA_SEGON_TRIMESTRE.setMaximumWidth(self.AMPLADA_DESPLEGABLES)

        self.DATA_TERCER_TRIMESTRE = QDateEdit()
        self.DATA_TERCER_TRIMESTRE.setDisplayFormat("dd/MM/yyyy")
        self.DATA_TERCER_TRIMESTRE.setCalendarPopup(True)
        self.DATA_TERCER_TRIMESTRE.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        # Definim el boto de desar:
        self.BOTO_DATES_DESAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/desar.svg"), text="Desar"
        )

        # Definim les etiquetes:
        ETIQUETA_SEGON = QLabel("Inici del segon trimestre")
        ETIQUETA_SEGON.setMaximumWidth(150)
        ETIQUETA_TERCER = QLabel("Inici del tercer trimestre")
        ETIQUETA_TERCER.setMaximumWidth(150)
        # Donem valors per si no hi han dades:
        if not self.calendari_editor_dates.dates:
            self.DATA_SEGON_TRIMESTRE.setDate(QDate.currentDate())
            self.DATA_TERCER_TRIMESTRE.setDate(QDate.currentDate())
        else:
            data_segon_bbdd = dateutil.parser.parse(self.calendari_editor_dates.dates[0].dia).date()
            data_tercer_bbdd = dateutil.parser.parse(self.calendari_editor_dates.dates[1].dia).date()
            DATA_2N_FORMATQT = QDate(data_segon_bbdd)
            DATA_3ER_FORMATQT = QDate(data_tercer_bbdd)
            self.DATA_SEGON_TRIMESTRE.setDate(DATA_2N_FORMATQT)
            self.DATA_TERCER_TRIMESTRE.setDate(DATA_3ER_FORMATQT)
        # Conectem amb la funcio per garantir resultats coherents:
        self.DATA_SEGON_TRIMESTRE.dateChanged.connect(self.coherencia_dates_trimestre)
        self.DATA_TERCER_TRIMESTRE.dateChanged.connect(self.coherencia_dates_trimestre)
        self.BOTO_DATES_DESAR.clicked.connect(self.modificacio_dates)
        # Determinem els elements que apareixen al widget:
        DISTRIBUCIO.addWidget(ETIQUETA_SEGON, 0, 0)
        DISTRIBUCIO.addWidget(self.DATA_SEGON_TRIMESTRE, 0, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_TERCER, 1, 0)
        DISTRIBUCIO.addWidget(self.DATA_TERCER_TRIMESTRE, 1, 1)
        DISTRIBUCIO.addWidget(self.BOTO_DATES_DESAR, 2, 0, 2, 0)

    def coherencia_dates_trimestre(self) -> object:
        """Funcio per garantir que la data del tercer trimestre sempre sigui, com a minim, un dia mes, que la del
        segon."""
        if self.DATA_SEGON_TRIMESTRE.date() >= self.DATA_TERCER_TRIMESTRE.date():
            data_3er = self.DATA_SEGON_TRIMESTRE.date().addDays(1)
            self.DATA_TERCER_TRIMESTRE.setDate(data_3er)
        elif self.DATA_TERCER_TRIMESTRE.date() <= self.DATA_SEGON_TRIMESTRE.date():
            data_2n = self.DATA_TERCER_TRIMESTRE.date().addDays(-1)
            self.DATA_SEGON_TRIMESTRE.setDate(data_2n)

    def modificacio_dates(self):
        """
        Analitza les dates dels components i actualitza els registres o en crea de nous, segons correspongui.
        :arg
        Valors actuals de les caselles d'edicio de data, s'executa al apretar el boto desar.
        :return:
        Fals si no s'ha pogut realitzar l'operacio corresponent a la base de dades.
        Veritat si s'han pogut realitzar.
        """
        estat_actualitzacio = True
        estat_creacio = True
        # Capturem la data del control i la convertim a format ISO:
        data2n = self.DATA_SEGON_TRIMESTRE.date().toPython()

        data3er = self.DATA_TERCER_TRIMESTRE.date().toPython()
        if self.calendari_editor_dates.dates:
            # Agafem la vriable dia de l'objecte DataGuiComm i el convertim a data de Python
            data_original_2n = dateutil.parser.parse(self.calendari_editor_dates.dates[0].dia).date()
            data_original_2n_id = self.calendari_editor_dates.dates[0].id
            data_original_3er = dateutil.parser.parse(self.calendari_editor_dates.dates[1].dia).date()
            data_original_3er_id = self.calendari_editor_dates.dates[1].id
            missatge_actualitzacio = []
            if data_original_2n != data2n:
                missatge_actualitzacio.append(DataGuiComm(data_original_2n_id, data2n.isoformat()))
            if data_original_3er != data3er:
                missatge_actualitzacio.append(DataGuiComm(data_original_3er_id, data3er.isoformat()))
            if len(missatge_actualitzacio) > 0:
                estat_actualitzacio = self.calendari_editor_dates.actualitza_dates(
                    missatge_actualitzacio
                )
        else:
            llista_noves_dates = [data2n.isoformat(), data3er.isoformat()]
            missatge_creacio = [DataNova(item) for item in llista_noves_dates]
            estat_creacio = Calendaritzador(1).registra_dates(missatge_creacio)
        if estat_creacio:
            return estat_creacio
        elif estat_actualitzacio:
            return estat_actualitzacio


class CreadorRegistres(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.AMPLADA_ETIQUETES = 75
        self.AMPLADA_DESPLEGABLES = 200
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.setLayout(DISTRIBUCIO)
        ETIQUETA_ALUMNES = QLabel("Alumnes")
        ETIQUETA_ALUMNES.setMaximumWidth(self.AMPLADA_ETIQUETES)
        self.SELECTOR_ALUMNES = QComboBox()
        self.SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        if obtenir_llistat_alumnes():
            self.SELECTOR_ALUMNES.addItems(obtenir_llistat_alumnes())
        self.resultat_creacio = None
        ETIQUETA_CATEGORIA = QLabel("Motiu:")
        ETIQUETA_CATEGORIA.setMaximumWidth(self.AMPLADA_ETIQUETES)
        self.SELECTOR_CATEGORIA = QComboBox()
        self.SELECTOR_CATEGORIA.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        if obtenir_categories():
            self.SELECTOR_CATEGORIA.addItems(obtenir_categories())
        ETIQUETA_DATES = QLabel("Data:")
        self.SELECTOR_DATES = QDateEdit()
        self.SELECTOR_DATES.setDisplayFormat("dd/MM/yyyy")
        self.SELECTOR_DATES.setCalendarPopup(True)
        self.SELECTOR_DATES.setDate(QDate.currentDate())
        self.SELECTOR_DATES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        ETIQUETA_DESCRIPCIO = QLabel("Descripcio: ")
        self.EDICIO_DESCRIPCIO = QTextEdit()

        self.BOTO_DESAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/desar.svg"), text="Desar"
        )
        self.BOTO_DESAR.setIconSize(QSize(24, 24))
        self.BOTO_DESAR.setToolTip("Desar")
        self.BOTO_DESAR.setFlat(True)
        self.BOTO_DESAR.setEnabled(False)
        self.EDICIO_DESCRIPCIO.setMaximumWidth(300)
        self.EDICIO_DESCRIPCIO.setMaximumHeight(200)
        DISTRIBUCIO.addWidget(ETIQUETA_ALUMNES, 0, 0)
        DISTRIBUCIO.addWidget(self.SELECTOR_ALUMNES, 0, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_CATEGORIA, 1, 0)
        DISTRIBUCIO.addWidget(self.SELECTOR_CATEGORIA, 1, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_DATES, 2, 0)
        DISTRIBUCIO.addWidget(self.SELECTOR_DATES, 2, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_DESCRIPCIO, 3, 0)
        DISTRIBUCIO.addWidget(self.EDICIO_DESCRIPCIO, 3, 1)
        DISTRIBUCIO.addWidget(self.BOTO_DESAR, 4, 0, 2, 0)
        self.EDICIO_DESCRIPCIO.textChanged.connect(self.actualitzar_descripcio)
        self.BOTO_DESAR.clicked.connect(self.desar_registre)

    def actualitzar_descripcio(self):
        """Bloqueja el boto desar si no hi ha descripcio."""
        if self.EDICIO_DESCRIPCIO.toPlainText() == "" or obtenir_llistat_alumnes() is False:
            self.BOTO_DESAR.setEnabled(False)
        else:
            self.BOTO_DESAR.setEnabled(True)

    def desar_registre(self):
        alumne = self.SELECTOR_ALUMNES.currentText()
        categoria = self.SELECTOR_CATEGORIA.currentText()
        data = self.SELECTOR_DATES.date().toString("yyyy-MM-dd")
        descripcio = self.EDICIO_DESCRIPCIO.toPlainText()
        self.EDICIO_DESCRIPCIO.clear()
        self.BOTO_DESAR.setEnabled(False)
        missatge_creacio_output = []
        registre_individual = [alumne, categoria, data, descripcio]
        for persona in CapEstudis(1).alumnat:
            if persona.nom == registre_individual[0]:
                registre_individual[0] = persona
        for motiu in Classificador(1).categories:
            if motiu.nom == registre_individual[1]:
                registre_individual[1] = motiu
        registre_individual = Registres_gui_nou(registre_individual[0], registre_individual[1], registre_individual[2],
                                                registre_individual[3])
        missatge_creacio_output.append(registre_individual)
        self.resultat_creacio = Comptable(1).crear_registre(missatge_creacio_output)


class EditorAlumnes(QtWidgets.QWidget):
    def __init__(self, parent=None, dades_alumnes=None):
        self.confirmacio_eliminar = None
        self.dades_model_transformades = None
        self.dades_originals_transformades = None
        self.titol_carpeta = "Selecciona carpeta"
        self.cap_edicio_alumnes = CapEstudis(1)
        QtWidgets.QWidget.__init__(self, parent)
        self.AMPLADA_ETIQUETES = 75
        self.AMPLADA_DESPLEGABLES = 200
        DISTRIBUCIO = QHBoxLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.setLayout(DISTRIBUCIO)
        self.TAULA_ALUMNES = QTableWidget(0, 2)
        self.files_control_taula = None
        self.etiquetes_columnes = ["ID", "Alumne"]
        self.TAULA_ALUMNES.setColumnHidden(0, True)
        self.TAULA_ALUMNES.setHorizontalHeaderLabels(self.etiquetes_columnes)
        self.TAULA_ALUMNES.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.TAULA_ALUMNES.setSelectionMode(QAbstractItemView.SingleSelection)
        self.TAULA_ALUMNES.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.TAULA_ALUMNES.setUpdatesEnabled(True)
        self.INDICADOR_ELIMINAT = None
        self.omplir_taula()
        # Creem els botons:
        estil_botons = "QPushButton { text-align: left; }"
        self.BOTO_IMPORTAR = QPushButton(icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/document-import-symbolic.svg"),
                                         text="Importar des\nd'arxiu")
        self.BOTO_IMPORTAR.setStyleSheet(estil_botons)
        self.BOTO_IMPORTAR.setIconSize(QSize(24, 24))
        self.BOTO_DESAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/desar.svg"), text="Desar"
        )
        self.BOTO_DESAR.setIconSize(QSize(24, 24))
        self.BOTO_DESAR.setStyleSheet(estil_botons)
        self.BOTO_AFEGIR = QPushButton(
            icon=QIcon(
                f"{AjudantDirectoris(1).ruta_icones}/value-increase-symbolic.svg"
            ),
            text="Afegir",
        )
        self.BOTO_AFEGIR.setIconSize(QSize(24, 24))
        self.BOTO_AFEGIR.setStyleSheet(estil_botons)
        self.BOTO_ELIMINAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/edit-delete-symbolic.svg"),
            text="Eliminar",
        )
        self.BOTO_ELIMINAR.setIconSize(QSize(24, 24))
        self.BOTO_ELIMINAR.setStyleSheet(estil_botons)
        DISTRIBUCIO_BOTONS = QVBoxLayout()
        DISTRIBUCIO_BOTONS.setAlignment(Qt.AlignTop)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_IMPORTAR)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_AFEGIR)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_ELIMINAR)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_DESAR)
        DISTRIBUCIO.addWidget(self.TAULA_ALUMNES)
        DISTRIBUCIO.addLayout(DISTRIBUCIO_BOTONS)
        # Connectem els botons:
        self.BOTO_IMPORTAR.clicked.connect(self.importar_arxius)
        self.BOTO_AFEGIR.clicked.connect(self.afegir_alumne_boto)
        self.BOTO_ELIMINAR.clicked.connect(self.eliminar_alumne)
        self.BOTO_DESAR.clicked.connect(self.alteracio_alumnes)
        self.TAULA_ALUMNES.doubleClicked.connect(self.modificar_alumne)

    def omplir_taula(self):
        dades_bbdd = obtenir_registres_alumnes()
        if dades_bbdd:
            self.files_control_taula = len(dades_bbdd)
            self.afegir_alumnes_general(dades_bbdd)

    def alteracio_alumnes(self):
        """Compara els registres d'alumnes de la gui i els originals, i els classifica per a modificar, eliminar o
        crear-ne un de nou, si correspon. I executa l'operacio corresponent a la base de dades"""
        # LLegim les dades de la base de dades:
        dades_originals = obtenir_registres_alumnes()
        dades_taula = []
        alumnes_eliminats = []
        alumnes_modificables = []
        nous_alumnes = []
        files_taula = self.TAULA_ALUMNES.rowCount()
        columnes_taula = self.TAULA_ALUMNES.columnCount()
        rang_files = list(range(files_taula))
        rang_columnes = list(range(columnes_taula))
        for fila in rang_files:
            registre_fila = []
            for columna in rang_columnes:
                valor_taula = self.TAULA_ALUMNES.item(fila, columna).text()
                if columna == 0 and valor_taula != "":
                    valor_taula = int(valor_taula)
                registre_fila.append(valor_taula)
            dades_taula.append(registre_fila)
        nous_alumnes = [alumne for alumne in dades_taula if alumne[0] == ""]
        alumnes_taula = [alumne for alumne in dades_taula if alumne[0] != ""]
        nous_alumnes = [AlumneNou(alumne[1]) for alumne in nous_alumnes]
        if dades_originals:
            llista_ids_originals = [alumne[0] for alumne in dades_originals]
            llista_ids_originals.sort()
            llista_ids_taula = [int(alumne[0]) for alumne in alumnes_taula]
            llista_ids_taula.sort()
            # Si l'id de l'alumne no esta entre els ID's dels alumnes originals, es que s'ha eliminat:
            alumnes_eliminats = [item for item in llista_ids_originals if item not in llista_ids_taula]
            alumnes_eliminats = [Alumne_comm(item[0], item[1]) for item in dades_originals if item[0] in
                                 alumnes_eliminats]
            # Si l'id de l'alumne esta entre els id's originals, comparem amb les dades originals:
            alumnes_modificables = [item for item in dades_taula if item[0] in llista_ids_originals]
            alumnes_modificables = [alumne for alumne in alumnes_modificables if alumne not in dades_originals]
            alumnes_modificables = [Alumne_comm(alumne[0], alumne[1]) for alumne in alumnes_modificables]
        if len(alumnes_modificables) > 0:
            self.cap_edicio_alumnes.actualitzar_alumnes(alumnes_modificables)
        if len(nous_alumnes) > 0:
            self.cap_edicio_alumnes.afegir_alumnes(nous_alumnes)
        if len(alumnes_eliminats) > 0:
            self.cap_edicio_alumnes.eliminar_alumnes(alumnes_eliminats)
        # Forcem el refresc de la taula:
        files_eliminar = list(range(self.TAULA_ALUMNES.rowCount()))
        self.TAULA_ALUMNES.setHorizontalHeaderLabels(self.etiquetes_columnes)
        for fila in files_eliminar:
            self.TAULA_ALUMNES.removeRow(fila)
        self.TAULA_ALUMNES.setRowCount(0)
        self.omplir_taula()

    def afegir_alumne_boto(self):
        dialeg = DialegAfegir(self)
        if dialeg.exec() == QDialog.Accepted:
            self.afegir_alumnes_general(dialeg.data)
            self.TAULA_ALUMNES.resizeColumnsToContents()

    def comprovacio_existent(self, noms_comprovar):
        """Comprova si una llista de noms conte alumnes ja existents i retorna els que no consten"""
        alumnes_existents = obtenir_llistat_alumnes()
        if isinstance(alumnes_existents, list):
            noms_comprovats = [nom for nom in noms_comprovar if nom not in alumnes_existents]
            return noms_comprovats
        return noms_comprovar

    def importar_arxius(self):
        arxiu = DialegSeleccioCarpeta().getOpenFileNames(self, self.titol_carpeta, filter="Arxius Excel o csv ("
                                                                                          "*csv *.xls *.xlsx *.ods)")
        # Obtenim la ruta a l'arxiu en format string:
        arxiu = os.path.normpath(arxiu[0][0])
        nom_arxiu = os.path.basename(arxiu)
        extensio_arxiu = os.path.splitext(os.path.normpath(arxiu))[1]
        if extensio_arxiu == ".csv":
            self.processar_importacio_csv(arxiu, nom_arxiu)
        elif extensio_arxiu in (".xls", ".ods"):
            self.processar_importacio_xls(arxiu)
        elif extensio_arxiu == ".xlsx":
            self.processar_importacio_xlsx(arxiu)

    def processar_importacio_csv(self, ruta_csv, nom_arxiu):
        dades_arxiu_csv = pyexcel_io.get_data(afile=ruta_csv)
        dades_arxiu_csv = dades_arxiu_csv[nom_arxiu]
        dades_arxiu_transformades = []
        for registre in dades_arxiu_csv:
            for element in registre:
                dades_arxiu_transformades.append(str(element).strip())
        dades_arxiu_transformades = self.comprovacio_existent(dades_arxiu_transformades)
        dades_arxiu_transformades = [["", item] for item in dades_arxiu_transformades]
        self.afegir_alumnes_general(dades_arxiu_transformades)

    def processar_importacio_xls(self, ruta_arxiu):
        """Processa un arxiu Excel amb extensio xls i els afegeix al widget"""
        dades_arxiu_excel = pyexcel_xls.get_data(ruta_arxiu)
        noms_fulls = list(dades_arxiu_excel.keys())
        dades_processar = []
        dades_format_llista = []
        for full in noms_fulls:
            dades_processar.extend(dades_arxiu_excel[full])
        for registre in dades_processar:
            for element in registre:
                dades_format_llista.append(str(element).strip())
        dades_format_llista = self.comprovacio_existent(dades_format_llista)
        dades_format_llista = [["", item] for item in dades_format_llista]
        self.afegir_alumnes_general(dades_format_llista)

    def processar_importacio_xlsx(self, ruta_arxiu):
        dades_xlsx = pyexcel_xlsxr.get_data(ruta_arxiu)
        noms_fulls = list(dades_xlsx.keys())
        dades_processar = []
        dades_format_llista = []
        for full in noms_fulls:
            dades_processar.extend(dades_xlsx[full])
        for registre in dades_processar:
            for element in registre:
                dades_format_llista.append(str(element).strip())
        dades_format_llista = self.comprovacio_existent(dades_format_llista)
        dades_format_llista = [["", item] for item in dades_format_llista]
        self.afegir_alumnes_general(dades_format_llista)

    def afegir_alumnes_general(self, dades_afegir: list):
        for alumne in dades_afegir:
            num_files_taula = self.TAULA_ALUMNES.rowCount()
            self.TAULA_ALUMNES.insertRow(num_files_taula)
            for element in alumne:
                columna = alumne.index(element)
                if isinstance(element, int):
                    element = str(element)
                self.TAULA_ALUMNES.setItem(num_files_taula, columna, QTableWidgetItem(element))
        self.TAULA_ALUMNES.resizeColumnsToContents()

    def eliminar_alumne(self):
        self.confirmacio_eliminar = DialegEliminar()
        self.INDICADOR_ELIMINAT = self.confirmacio_eliminar.Yes
        if self.confirmacio_eliminar.exec() == QMessageBox.Yes:
            index = self.TAULA_ALUMNES.currentIndex()
            self.TAULA_ALUMNES.removeRow(index.row())

    def modificar_alumne(self):
        # Editar un registre:
        index = self.TAULA_ALUMNES.currentIndex()
        self.TAULA_ALUMNES.edit(index)


class GeneradorInformesExportImport(QtWidgets.QWidget):
    """Classe per a generar informes i exportar/importar"""

    def __init__(self):
        super().__init__()
        self.importacio = None
        self.icona_carpeta = "inode-directory-symbolic.svg"
        self.titol_carpeta = "Selecciona carpeta"
        self.selcarpeta = None
        self.tipus_informes = None
        self.desti_json = None
        self.resultat_exportacio = None
        self.resultat_informes = None
        self.dates_informe = Calendaritzador(1).info_dates
        self.AMPLADA_DESPLEGABLES = 200
        self.resize(300, 300)
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.setLayout(DISTRIBUCIO)
        # Creem les opcions d'informe
        GRUP_TIPUS = QGroupBox()
        GRUP_TIPUS.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        GRUP_TIPUS.setTitle("Crear informes format Excel")
        GRUP_TIPUS.setFlat(True)
        GRUP_TIPUS_DISTRIBUCIO = QVBoxLayout()
        GRUP_TIPUS.setLayout(GRUP_TIPUS_DISTRIBUCIO)
        # Creem el grup d'exportacio i importacio:
        grup_export_import = QGroupBox()
        grup_export_import.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        grup_export_import.setTitle("Exportar/importar")
        grup_export_import.setFlat(True)
        grup_export_importdistribucio = QVBoxLayout()
        grup_export_import.setLayout(grup_export_importdistribucio)
        # Definim les opcions per a la creacio d’informes en Excel:
        self.informe_seleccionat: Union[QButtonGroup, QButtonGroup] = QButtonGroup()
        self.opcio_categories = QRadioButton("Categories")
        self.opcio_categories.setChecked(False)
        self.opcio_alumnes = QRadioButton("Per alumne")
        self.informe_seleccionat.setExclusive(True)
        self.informe_seleccionat.addButton(self.opcio_categories, 0)
        self.informe_seleccionat.addButton(self.opcio_alumnes, 1)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(self.opcio_categories)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(self.opcio_alumnes)
        # Creem les opcions per a l'exportacio o la importacio:
        self.tipus_accio_json = QButtonGroup()
        self.tipus_accio_json.setExclusive(True)
        self.opcio_exportar = QRadioButton("Exportar")
        self.opcio_importar = QRadioButton("Importar")
        self.tipus_accio_json.addButton(self.opcio_exportar, 0)
        self.tipus_accio_json.addButton(self.opcio_importar, 1)
        grup_export_importdistribucio.addWidget(self.opcio_exportar)
        grup_export_importdistribucio.addWidget(self.opcio_importar)
        # Creem el selector d'alumnes per a l'exportacio:
        self.exportimport_selector_alumnes = QComboBox()
        self.exportimport_selector_alumnes.addItem("* Tots *")
        self.exportimport_selector_alumnes.setVisible(False)
        # Creem els selectors d'informe en Excel:
        self.INFORMES_SELECTOR_ALUMNES = QComboBox()
        self.INFORMES_SELECTOR_ALUMNES.addItem("* Tots *")
        # Afegim les dades de la taula, si n'hi ha:
        self.INFORMES_SELECTOR_CATEGORIES = QComboBox()
        self.INFORMES_SELECTOR_CATEGORIES.addItem("* Totes *")

        self.INFORMES_SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.INFORMES_SELECTOR_ALUMNES.setVisible(False)
        self.INFORMES_SELECTOR_CATEGORIES.setVisible(False)
        self.INFORMES_SELECTOR_CATEGORIES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        # Creem els botons per a l'exportacio o importacio:
        self.export_seleccio_carpeta = QPushButton(
            QIcon(os.path.join(AjudantDirectoris(1).ruta_icones, self.icona_carpeta)), "")
        self.boto_exportar_json = QPushButton("Exportar")
        self.boto_exportar_json.setVisible(False)
        self.export_seleccio_carpeta.setVisible(False)
        self.import_seleccio_arxiu = QPushButton(
            QIcon(os.path.join(AjudantDirectoris(1).ruta_icones, self.icona_carpeta)), "Seleccioneu arxiu")
        self.import_seleccio_arxiu.setVisible(False)
        # Creem els botons per a la creacio d'informes en Excel:
        self.BOTON_INFORME = QPushButton("Generar informe")
        self.BOTON_INFORME.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.BOTON_INFORME.setVisible(False)
        self.BOTON_INFORME.setEnabled(False)
        self.SELECCIO_CARPETA = QPushButton(QIcon(os.path.join(AjudantDirectoris(1).ruta_icones,
                                                               self.icona_carpeta)), "")
        self.SELECCIO_CARPETA.setIconSize(QSize(24, 24))
        self.SELECCIO_CARPETA.setVisible(False)
        # Distribuim els elements:
        DISTRIBUCIO.addWidget(GRUP_TIPUS, 0, 0)
        DISTRIBUCIO.addWidget(grup_export_import, 0, 1)
        DISTRIBUCIO.addWidget(self.INFORMES_SELECTOR_ALUMNES, 1, 0)
        DISTRIBUCIO.addWidget(self.exportimport_selector_alumnes, 1, 1)
        DISTRIBUCIO.addWidget(self.INFORMES_SELECTOR_CATEGORIES, 2, 0)
        DISTRIBUCIO.addWidget(self.export_seleccio_carpeta, 2, 1)
        DISTRIBUCIO.addWidget(self.SELECCIO_CARPETA, 3, 0)
        DISTRIBUCIO.addWidget(self.boto_exportar_json, 3, 1)
        DISTRIBUCIO.addWidget(self.import_seleccio_arxiu, 3, 1)
        DISTRIBUCIO.addWidget(self.BOTON_INFORME, 4, 0)
        self.opcio_exportar.toggled.connect(self.seleccio_accio_json)
        self.opcio_importar.toggled.connect(self.seleccio_accio_json)
        self.opcio_alumnes.toggled.connect(self.seleccionar_informe)
        self.opcio_categories.toggled.connect(self.seleccionar_informe)
        self.BOTON_INFORME.clicked.connect(self.generar_informe)
        self.export_seleccio_carpeta.clicked.connect(self.seleccionar_carpeta_exportacio_json)
        self.import_seleccio_arxiu.clicked.connect(self.importar)
        self.SELECCIO_CARPETA.clicked.connect(self.seleccionar_carpeta_informes)
        self.boto_exportar_json.clicked.connect(self.exportar)
        self.destinacio_informes = None
        self.carpeta_exportacio = None
        self.arxiu_importacio = None

    def seleccionar_informe(self):
        self.informe_seleccionat.setExclusive(True)
        self.tipus_accio_json.setExclusive(False)
        self.opcio_exportar.setChecked(False)
        self.opcio_importar.setChecked(False)
        self.export_seleccio_carpeta.setVisible(False)
        self.exportimport_selector_alumnes.setVisible(False)
        self.boto_exportar_json.setVisible(False)
        self.import_seleccio_arxiu.setVisible(False)
        if self.informe_seleccionat.checkedId() == 0:
            self.BOTON_INFORME.setVisible(True)
            self.BOTON_INFORME.setEnabled(True)
            self.SELECCIO_CARPETA.setVisible(True)
            self.export_seleccio_carpeta.setVisible(False)
            self.tipus_informes = 0
            self.INFORMES_SELECTOR_CATEGORIES.setVisible(True)
            self.INFORMES_SELECTOR_ALUMNES.setVisible(False)
            self.INFORMES_SELECTOR_ALUMNES.setCurrentIndex(0)

        elif self.informe_seleccionat.checkedId() == 1:
            self.BOTON_INFORME.setVisible(True)
            self.SELECCIO_CARPETA.setVisible(True)
            self.tipus_informes = 1
            self.BOTON_INFORME.setEnabled(True)
            self.INFORMES_SELECTOR_CATEGORIES.setVisible(False)
            self.INFORMES_SELECTOR_ALUMNES.setVisible(True)
            self.INFORMES_SELECTOR_CATEGORIES.setCurrentIndex(0)

    def seleccio_accio_json(self):
        self.informe_seleccionat.setExclusive(False)
        self.tipus_accio_json.setExclusive(True)
        self.opcio_categories.setChecked(False)
        self.opcio_alumnes.setChecked(False)
        self.BOTON_INFORME.setVisible(False)
        self.SELECCIO_CARPETA.setVisible(False)
        self.INFORMES_SELECTOR_ALUMNES.setVisible(False)
        self.INFORMES_SELECTOR_CATEGORIES.setVisible(False)
        if self.tipus_accio_json.checkedId() == 0:
            self.exportimport_selector_alumnes.setVisible(True)
            self.export_seleccio_carpeta.setVisible(True)
            self.boto_exportar_json.setVisible(True)
            self.import_seleccio_arxiu.setVisible(False)
        elif self.tipus_accio_json.checkedId() == 1:
            self.exportimport_selector_alumnes.setVisible(False)
            self.boto_exportar_json.setVisible(False)
            self.export_seleccio_carpeta.setVisible(False)
            self.import_seleccio_arxiu.setVisible(True)

    def seleccionar_carpeta_exportacio_json(self):
        self.desti_json = DialegSeleccioCarpeta().getExistingDirectory(self, self.titol_carpeta)
        if self.desti_json:
            self.carpeta_exportacio = self.desti_json

    def seleccionar_carpeta_informes(self):
        """Funcio per a seleccionar la carpeta on es guardaran els informes."""
        self.selcarpeta = DialegSeleccioCarpeta().getExistingDirectory(self, self.titol_carpeta)
        if self.selcarpeta:
            self.destinacio_informes = self.selcarpeta

    def exportar(self):
        if self.carpeta_exportacio is None:
            self.resultat_exportacio = "nocarpeta"
        else:
            llistat_alumnes = []
            if self.exportimport_selector_alumnes.currentIndex() == 0:
                llistat_alumnes = CapEstudis(1).alumnat_registres
            else:

                alumne_seleccionat = self.exportimport_selector_alumnes.currentText()
                for alumne in CapEstudis(1).alumnat_registres:
                    if alumne.nom == alumne_seleccionat:
                        llistat_alumnes.append(alumne)
            resultat_exportacio = ExportadorImportador(1).exportacio(llistat_alumnes, self.carpeta_exportacio)
            if resultat_exportacio:
                self.resultat_exportacio = True
            elif resultat_exportacio is False:
                self.resultat_exportacio = False

    def importar(self):
        self.importacio = DialegSeleccioCarpeta().getOpenFileNames(self, self.titol_carpeta, filter="Arxius json("
                                                                                                    "*.json)")
        arxius_importacio = self.importacio[0]
        ExportadorImportador(1).importacio(arxius_importacio)

    def generar_informe(self):
        """Funcio per a generar un informe. Explicacio de la variable tipus informe: 0 si es de categories, 1 si es per
        alumne."""
        dades_registres = Comptable(1).obtenir_registres()
        alumnes_informe = CapEstudis(1).alumnat_registres
        carpeta_desti = self.destinacio_informes
        categories_registrades = Classificador(1).categories_registrades
        resposta = None
        if self.destinacio_informes is not None:
            if self.tipus_informes == 0:
                # Es un informe de categories:

                valor_actual = self.INFORMES_SELECTOR_CATEGORIES.currentText()
                categoria_informe = [categoria for categoria in categories_registrades if
                                     categoria.nom == valor_actual]
                if self.INFORMES_SELECTOR_CATEGORIES.currentIndex() != 0:
                    exportador = CreadorInformes(alumnes_informe, categoria_informe, dades_registres, carpeta_desti)
                else:
                    exportador = CreadorInformes(alumnes_informe, categories_registrades, dades_registres,
                                                 carpeta_desti)
                resposta = exportador.export_categories()
            elif self.tipus_informes == 1:
                # Es un informe per alumne:
                dates_informe = Calendaritzador(1).info_dates
                valor_actual = self.INFORMES_SELECTOR_ALUMNES.currentText()
                categories_enviar = Classificador(1).categories
                if self.INFORMES_SELECTOR_ALUMNES.currentIndex() != 0:
                    # Enviem tan sols la informacio de l'alumne en concret, no tot el registre:
                    alumnes_informe = [alumne for alumne in alumnes_informe if alumne.nom == valor_actual]
                    dades_enviar = [registre for registre in dades_registres if registre.alumne.nom == valor_actual]
                else:
                    dades_enviar = dades_registres
                exportador = CreadorInformes(alumnes_informe, categories_enviar, dades_enviar, carpeta_desti)
                resposta = exportador.export_alumne(dates_informe)
            if resposta:
                self.resultat_informes = True


class EditorRegistres(QtWidgets.QWidget):
    def __init__(self):
        super(EditorRegistres, self).__init__()
        self.AMPLADA_DESPLEGABLES = 200
        self.TAULA = QTableWidget()
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.setLayout(DISTRIBUCIO)
        self.seleccio_alumnes = QComboBox()
        self.seleccio_categories = QComboBox()
        self.seleccio_alumnes.addItem("* Filtrar per alumne *")
        self.seleccio_categories.addItem("* Filtrar per categoria *")
        if obtenir_llistat_categories_registrades():
            self.seleccio_categories.addItems(obtenir_llistat_categories_registrades())
        if obtenir_llistat_alumnes_registrats():
            self.seleccio_alumnes.addItems(obtenir_llistat_alumnes_registrats())
        self.seleccio_alumnes.setMaximumWidth(300)
        self.boto_desar = QPushButton(icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/desar.svg"), text="Desar canvis")
        self.boto_eliminar = QPushButton(icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/edit-delete-symbolic.svg"),
                                         text="Eliminar")
        self.noms_columnes = ["ID", "Alumne", "Motiu", "Data", "Descripció"]
        if obtenir_llistat_registres() not in [None, False]:
            self.omplir_taula()
        self.TAULA.setHorizontalHeaderLabels(self.noms_columnes)
        # Possibilitat d'establir un ComboBox:
        # https://stackoverflow.com/questions/48105026/how-to-update-a-qtableview-cell-with-a-qcombobox-selection
        self.TAULA.setColumnHidden(0, True)
        self.TAULA.setWordWrap(True)
        self.TAULA.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.TAULA.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.TAULA.setSelectionMode(QAbstractItemView.SingleSelection)
        self.TAULA.setColumnWidth(4, self.AMPLADA_DESPLEGABLES)
        self.TAULA.resizeRowsToContents()
        self.TAULA.resizeColumnToContents(1)
        self.TAULA.resizeColumnToContents(2)
        self.TAULA.resizeColumnToContents(3)
        self.TAULA.setSortingEnabled(True)
        self.TAULA.setItemDelegateForColumn(1, DelegatAlumnes(self))
        self.TAULA.setItemDelegateForColumn(2, DelegatCategories(self))
        self.TAULA.setItemDelegateForColumn(3, DelegatDates(self))
        DISTRIBUCIO.addWidget(self.seleccio_alumnes, 0, 0)
        DISTRIBUCIO.addWidget(self.seleccio_categories, 0, 1)
        DISTRIBUCIO.addWidget(self.boto_eliminar, 0, 2)
        DISTRIBUCIO.addWidget(self.boto_desar, 0, 3)
        DISTRIBUCIO.addWidget(self.TAULA, 1, 0, 1, 0)
        self.seleccio_alumnes.currentTextChanged.connect(self.visualitzacio_filtre_alumnes)
        self.seleccio_categories.currentTextChanged.connect(self.visualitzacio_filtre_categories)
        self.boto_desar.clicked.connect(self.alteracio_registres)
        self.boto_eliminar.clicked.connect(self.eliminar_fila_taula)

    def eliminar_fila_taula(self):
        self.TAULA.removeRow(self.TAULA.currentRow())

    def omplir_taula(self):
        self.TAULA.setHorizontalHeaderLabels(self.noms_columnes)
        self.TAULA.setColumnHidden(0, True)
        self.TAULA.setWordWrap(True)
        self.TAULA.resizeColumnsToContents()
        if obtenir_llistat_registres():
            dades = obtenir_llistat_registres()
            files = len(dades)
            columnes = len(dades[0])
            self.TAULA.setRowCount(files)
            self.TAULA.setColumnCount(columnes)
            rang_files = range(files)
            rang_columnes = range(columnes)
            desplegable_taula_alumnes = QComboBox()
            desplegable_taula_alumnes.addItems(obtenir_llistat_alumnes())
            desplegable_taula_categories = QComboBox()
            desplegable_taula_categories.addItems(obtenir_categories())
            for fila in rang_files:
                for columna in rang_columnes:
                    valor = dades[fila][columna]
                    if isinstance(valor, datetime.date):
                        nou_item = QTableWidgetItem()
                        valor = QDate(valor)
                        nou_item.setData(Qt.DisplayRole, valor)
                        self.TAULA.setItem(fila, columna, nou_item)
                    else:
                        nou_item = QTableWidgetItem(str(valor))
                        self.TAULA.setItem(fila, columna, nou_item)
            self.TAULA.resizeColumnsToContents()

    def alteracio_registres(self):
        """Funcio per a comparar els registres de la taula quan hi ha canvis i gestionar-los, tant si s'eliminen com
        si s'afegien. """
        dades_originals = obtenir_llistat_registres()
        rang_files_taula = range(self.TAULA.rowCount())
        rang_columnes_taula = range(self.TAULA.columnCount())
        registres_eliminats = []
        registres_actualitzats = []
        llista_dades_model = []
        # Convertim les dades del model en llista de llistes per poder comparar:
        for fila in rang_files_taula:
            fila_taula = []
            for columna in rang_columnes_taula:
                valor = None
                if columna == 0:
                    valor = int(self.TAULA.item(fila, columna).data(0))
                elif columna == 3:
                    valor = self.TAULA.item(fila, columna).data(0).toPython()
                else:
                    valor = self.TAULA.item(fila, columna).data(0)
                fila_taula.append(valor)
            llista_dades_model.append(fila_taula)

        llista_ids_originals: list = [ref[0] for ref in dades_originals]
        llista_ids_model: list = [ref[0] for ref in llista_dades_model]
        # Comparem els ids, si n'hi ha menys, implica que s'ha eliminat algun:
        if len(llista_ids_model) < len(llista_ids_originals):
            ids_eliminats = [item for item in llista_ids_originals if item not in llista_ids_model]
            registres_eliminats = [item for item in dades_originals if item[0] in ids_eliminats]
        dades_originals.sort(key=lambda x: x[0])
        # Ordenem les dades del model per id:
        llista_dades_model.sort(key=lambda x: x[0])
        registres_actualitzats = [element_taula for element_taula in llista_dades_model if element_taula not in
                                  dades_originals]
        # Comprovem si hi han actualitzacions o eliminacions i passem l'ordre corresponent:
        if len(registres_eliminats) > 0:
            self.eliminar_registres(registres_eliminats)
        if len(registres_actualitzats) > 0:
            self.actualitzar_registres(registres_actualitzats)

    def eliminar_registres(self, registres_eliminats):
        """Funcio per a eliminar registres de la base de dades."""
        missatge_eliminar = []
        for registre in registres_eliminats:
            eliminacio_registre = self.transformar_gui_a_bbdd(registre)
            missatge_eliminar.append(eliminacio_registre)
        Comptable(1).eliminar_registre(missatge_eliminar)

    def actualitzar_registres(self, registres_actualitzats):
        """Funcio per a actualitzar registres de la base de dades."""
        missatge_actualitzacio = []
        for registre in registres_actualitzats:
            actualitzacio_registre = self.transformar_gui_a_bbdd(registre)
            missatge_actualitzacio.append(actualitzacio_registre)
        Comptable(1).actualitzar_registres(missatge_actualitzacio)

    def transformar_gui_a_bbdd(self, dades: list):
        """Funcio per a transformar les dades de la GUI a la BBDD."""
        if not isinstance(dades, list):
            raise TypeError("S'ha de passar una llista")
        alumne = None
        categoria_enviar = None
        # Transformem la data:
        id_registre = dades[0]
        for persona in CapEstudis(1).alumnat:
            if persona.nom == dades[1]:
                alumne = persona
        for categoria in Classificador(1).info_categories:
            if categoria.nom == dades[2]:
                categoria_enviar = categoria
        data = dades[3].strftime("%Y-%m-%d")
        descripcio = dades[4]
        # Guardem la dada:
        resultat = Registresguicomm(id_registre, alumne, categoria_enviar, data, descripcio)
        return resultat

    def visualitzacio_filtre_alumnes(self):
        """Comportament quan s'esta reallitzant un filtre per alumnes al widget amb el llistat"""
        valor_actual_desplegable = self.seleccio_alumnes.currentText()
        self.seleccio_categories.setCurrentIndex(0)
        if self.seleccio_alumnes.currentIndex() == 0:
            for fila in range(self.TAULA.rowCount()):
                self.TAULA.showRow(fila)
            self.TAULA.showColumn(1)
            self.TAULA.showColumn(2)
            self.seleccio_categories.setCurrentIndex(0)
            self.TAULA.resizeRowsToContents()
        else:
            for fila in range(self.TAULA.rowCount()):
                self.TAULA.showRow(fila)
            registres_mostrar = self.TAULA.findItems(valor_actual_desplegable, Qt.MatchExactly)
            files_mostrar = [element.row() for element in registres_mostrar]
            files_amagar = [fila for fila in range(self.TAULA.rowCount()) if fila not in files_mostrar]
            for fila in files_amagar:
                self.TAULA.hideRow(fila)
            self.TAULA.showColumn(2)
            self.TAULA.hideColumn(1)
            self.TAULA.resizeRowsToContents()

    def visualitzacio_filtre_categories(self):
        categoria_seleccionada = self.seleccio_categories.currentText()
        if self.seleccio_categories.currentIndex() == 0:
            for fila in range(self.TAULA.rowCount()):
                self.TAULA.showRow(fila)
            self.TAULA.showColumn(1)
            self.TAULA.showColumn(2)
            self.seleccio_categories.setCurrentIndex(0)
            self.TAULA.resizeRowsToContents()
        else:
            for fila in range(self.TAULA.rowCount()):
                self.TAULA.showRow(fila)
            registres_mostrar = self.TAULA.findItems(categoria_seleccionada, Qt.MatchExactly)
            files_mostrar = [element.row() for element in registres_mostrar]
            files_amagar = [fila for fila in range(self.TAULA.rowCount()) if fila not in files_mostrar]
            for fila in files_amagar:
                self.TAULA.hideRow(fila)
            self.seleccio_alumnes.setCurrentIndex(0)
            self.TAULA.hideColumn(2)
            self.TAULA.resizeRowsToContents()
