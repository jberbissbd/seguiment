import os
import sys
from datetime import date, timedelta, datetime
from typing import List, Any, Union
from src.agents.formats import Data, Registre_entrada, Alumne, Categoria, Registre_sortida
from src.proves_dao.comptable import Comptable, Classificador, Calendaritzador, CapEstudis
import PySide6.QtCore
import PySide6.QtGui
import dateutil
from PySide6 import QtCharts, QtSql, QtCore
from PySide6.QtSql import QSqlTableModel, QSqlDatabase, QSqlDriver
from PySide6.QtCore import QSize, Qt, QAbstractTableModel, QDate
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                               QFileDialog, QToolBar, QTableView, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QMessageBox, QPushButton, QStackedLayout, QStackedWidget, QButtonGroup,
                               QTextEdit, QVBoxLayout, QWidget, QAbstractItemView, QWizard, QWizardPage, QTabWidget,
                               QHeaderView, QSizePolicy, QStyle, QRadioButton, QGroupBox, QTableWidget)


def sortir():
    app.quit()


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                # See below for the nested-list data structure.
                # .row() indexes into the outer list,
                # .column() indexes into the sub-list
                value = self._data[index.row()][index.column()]
                return value

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def flags(self, index):
        if index.column() != 2:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.BOTO_DATES = None
        self.BOTO_INFORMES = None
        self.TAULA_MODEL = None
        self.VISUALITZAR_EDITAR = None
        self.informe_seleccionat = None
        self.tipus_informes = 0
        self.AMPLADA_ETIQUETES = 75
        self.AMPLADA_DESPLEGABLES = 200
        self.CREACIO = None
        self.BOTO_CREAR = None
        self.WIDGET_CENTRAL = None
        self.BOTO_SORTIR = None
        self.BARRA_EINES_DISTIBUCIO = None
        self.WIDGET_PRINCIPAL = None
        self.BOTO_VISUALITZAR = None
        self.crear_registres = None
        self.cap = CapEstudis()
        self.categoritzador = Classificador()
        self.calendari = Calendaritzador()
        self.acces_registres = Comptable()
        self.configuracio_interficie()

    def configuracio_interficie(self):
        self.setWindowTitle("Seguiment d'alumnes")
        self.resize(600, 500)
        # Configurem distribucio principal:
        # Configurem Widget principal:
        self.WIDGET_PRINCIPAL = QWidget()
        self.WIDGET_CENTRAL = QStackedWidget()
        DISTRIBUCIO_PRINCIPAL = QVBoxLayout()
        self.WIDGET_PRINCIPAL.setLayout(DISTRIBUCIO_PRINCIPAL)
        self.setCentralWidget(self.WIDGET_PRINCIPAL)
        self.widget_creacio()
        self.widget_visualitzacio()
        self.widget_dates()
        self.widget_informes()
        # Introduim la barra d'eines:

        self.BARRA_EINES_DISTIBUCIO = QToolBar()
        DISTRIBUCIO_PRINCIPAL.addWidget(self.BARRA_EINES_DISTIBUCIO)
        DISTRIBUCIO_PRINCIPAL.addWidget(self.WIDGET_CENTRAL)

        # Definim botons i les seves propietats:
        self.BOTO_CREAR = QPushButton(self, icon=QIcon("icones/system-switch-user-symbolic.svg"), text="Crear")

        self.BOTO_CREAR.setIconSize(QSize(32, 32))
        self.BOTO_CREAR.setToolTip("Crear un nou registre")
        self.BOTO_CREAR.setFlat(True)

        self.BOTO_VISUALITZAR = QPushButton(self, icon=QIcon("icones/document-properties-symbolic.svg"),
                                            text="Visualitzar/Editar")
        self.BOTO_VISUALITZAR.setIconSize(QSize(32, 32))
        self.BOTO_VISUALITZAR.setToolTip("Visualitzar/Editar un registre")
        self.BOTO_VISUALITZAR.setFlat(True)
        self.BOTO_DATES = QPushButton(self, icon=QIcon("icones/office-calendar-symbolic.svg"), text="Dates")
        self.BOTO_DATES.setIconSize(QSize(32, 32))
        self.BOTO_DATES.setToolTip("Dates trimestre")
        self.BOTO_DATES.setFlat(True)
        self.BOTO_INFORMES = QPushButton(self, icon=QIcon("icones/document-save-symbolic.svg"), text="Informes")
        self.BOTO_INFORMES.setIconSize(QSize(32, 32))
        self.BOTO_INFORMES.setToolTip("Informes")
        self.BOTO_INFORMES.setFlat(True)

        self.BOTO_SORTIR = QPushButton(self, icon=QIcon("icones/application-exit-symbolic.svg"), text="Sortir")
        self.BOTO_SORTIR.setIconSize(QSize(32, 32))
        # Afegim els botons a la barra d'eines:
        self.BARRA_EINES_DISTIBUCIO.addWidget(self.BOTO_CREAR)
        self.BARRA_EINES_DISTIBUCIO.addWidget(self.BOTO_VISUALITZAR)
        self.BARRA_EINES_DISTIBUCIO.addWidget(self.BOTO_DATES)
        self.BARRA_EINES_DISTIBUCIO.addWidget(self.BOTO_INFORMES)
        self.BARRA_EINES_DISTIBUCIO.addSeparator()
        self.BARRA_EINES_DISTIBUCIO.addWidget(self.BOTO_SORTIR)
        # Definim widgets:

        # Afegim pestanyes, un widget per cadascuna:
        self.WIDGET_CENTRAL.addWidget(self.CREACIO)
        self.WIDGET_CENTRAL.addWidget(self.VISUALITZAR_EDITAR)
        self.WIDGET_CENTRAL.addWidget(self.DATES)
        self.WIDGET_CENTRAL.addWidget(self.INFORME)

        # Connectem botons:
        self.BOTO_CREAR.clicked.connect(self.mostrar_creacio)
        self.BOTO_VISUALITZAR.clicked.connect(self.mostrar_visualitzacio)
        self.BOTO_DATES.clicked.connect(self.mostrar_dates)
        self.BOTO_INFORMES.clicked.connect(self.mostrar_informes)
        self.BOTO_SORTIR.clicked.connect(sortir)

    def widget_creacio(self):
        # Creem el widget de creacio de nous registres:
        self.CREACIO = QWidget()
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        DISTRIBUCIO.setVerticalSpacing(10)
        self.CREACIO.setLayout(DISTRIBUCIO)
        ETIQUETA_ALUMNES = QLabel("Alumnes")
        ETIQUETA_ALUMNES.setMaximumWidth(self.AMPLADA_ETIQUETES)
        SELECTOR_ALUMNES = QComboBox()
        SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes())
        SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        ETIQUETA_CATEGORIA = QLabel("Motiu:")
        ETIQUETA_CATEGORIA.setMaximumWidth(self.AMPLADA_ETIQUETES)
        SELECTOR_CATEGORIA = QComboBox()
        SELECTOR_CATEGORIA.addItems(self.obtenir_categories())
        SELECTOR_CATEGORIA.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        ETIQUETA_DATES = QLabel("Data:")
        SELECTOR_DATES = QDateEdit()
        SELECTOR_DATES.setDisplayFormat(u"dd/MM/yyyy")
        SELECTOR_DATES.setCalendarPopup(True)
        SELECTOR_DATES.setDate(QDate.currentDate())
        SELECTOR_DATES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        ETIQUETA_DESCRIPCIO = QLabel("Descripcio: ")
        EDICIO_DESCRIPCIO = QTextEdit()
        EDICIO_DESCRIPCIO.setMaximumWidth(300)
        EDICIO_DESCRIPCIO.setMaximumHeight(350)
        DISTRIBUCIO.addWidget(ETIQUETA_ALUMNES, 0, 0)
        DISTRIBUCIO.addWidget(SELECTOR_ALUMNES, 0, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_CATEGORIA, 1, 0)
        DISTRIBUCIO.addWidget(SELECTOR_CATEGORIA, 1, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_DATES, 2, 0)
        DISTRIBUCIO.addWidget(SELECTOR_DATES, 2, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_DESCRIPCIO, 3, 0)
        DISTRIBUCIO.addWidget(EDICIO_DESCRIPCIO, 3, 1)

    def widget_visualitzacio(self):
        self.VISUALITZAR_EDITAR = QWidget()
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.VISUALITZAR_EDITAR.setLayout(DISTRIBUCIO)
        DESPLEGABLE_SELECCIO = QComboBox()
        DESPLEGABLE_SELECCIO.addItem("* Selecciona un alumne *")
        DESPLEGABLE_SELECCIO.addItems(self.obtenir_llistat_alumnes_registrats())
        DESPLEGABLE_SELECCIO.setMaximumWidth(300)
        BOTO_DESAR = QPushButton(icon=QIcon("icones/document-save-symbolic.svg"), text="Desar canvis")
        BOTO_DESAR.clicked.connect(self.introduccio_registres)
        self.TAULA_MODEL = TableModel(self.obtenir_llistat_registres())
        self.columnes_model: int = self.TAULA_MODEL.columnCount(1)
        self.files_model: int = self.TAULA_MODEL.rowCount(1)
        self.TAULA = QTableView()
        self.TAULA.setModel(self.TAULA_MODEL)
        DISTRIBUCIO.addWidget(DESPLEGABLE_SELECCIO, 0, 0)
        DISTRIBUCIO.addWidget(BOTO_DESAR, 0, 1)
        DISTRIBUCIO.addWidget(self.TAULA, 1, 0, 1, 0)

    def introduccio_registres(self):
        """Funcio per a comparar els registres de la taula i gestionar-los, tant si s'eliminen com si s'afegien."""
        model_comparacio = self.TAULA.model()
        dades_originals = self.obtenir_llistat_registres()
        llista_ids_originals: list = [ref[0] for ref in dades_originals]
        llista_ids_model = []
        registres_eliminats: list = []
        registres_actualitzats: list = []
        rang_files = list(range(self.TAULA.model().rowCount(1)))
        rang_columnes = list(range(self.TAULA.model().columnCount(1)))
        # Guardem els ids de les files del model i comprovem que no hagi cap id que falti:
        for fila in rang_files:
            llista_ids_model.append(model_comparacio.data(model_comparacio.index(fila, 0)))
        # Ordenem les llistes per id:
        llista_ids_originals.sort()
        llista_ids_model.sort()
        dades_originals.sort(key=lambda x: x[0])
        # Convertim les dades del model en llista de llistes per poder comparar::
        llista_dades_model = []
        for row in range(0, self.files_model):
            fila_model = []
            for column in range(0, self.columnes_model):
                fila_model.append(model_comparacio.data(model_comparacio.index(row, column)))
            llista_dades_model.append(fila_model)
        # Ordenem les dades del model per id:
        llista_dades_model.sort(key=lambda x: x[0])
        # Comparem els ids de les files del model amb els ids de les files originals:
        for item in rang_files:
            if llista_ids_originals[item] != llista_ids_model[item]:
                registres_eliminats.append(llista_ids_originals[item])
                item += 1
                continue
            # Un cop sapigut aixo, comprovem les actualitzacions:
            else:
                # Comprovem els registres un per un. Si son diferents, guardem els canvis:
                if dades_originals[item] != llista_dades_model[item]:
                    registres_actualitzats.append(llista_dades_model[item])
                    continue
        # Comprovem si hi han actualitzacions o eliminacions i passem l'ordre corresponent:
        if registres_eliminats:
            self.eliminar_registres(registres_eliminats)
        if registres_actualitzats:
            self.actualitzar_registres(registres_actualitzats)

    def eliminar_registres(self, registres_eliminats):
        """Funcio per a eliminar registres de la base de dades."""
        for registre in registres_eliminats:
            self.CONTROLADOR.eliminar_registre(registre)
            self.TAULA_MODEL.eliminar_registre(registre)
            self.TAULA_MODEL.layoutChanged.emit()

    def actualitzar_registres(self, registres_actualitzats):
        """Funcio per a actualitzar registres de la base de dades."""
        for registre in registres_actualitzats:
            print(registre)
            # self.TAULA_MODEL.layoutChanged.emit()

    def widget_dates(self):
        self.DATES = QWidget()
        DISTRIBUCIO = QVBoxLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.DATES.setLayout(DISTRIBUCIO)
        DESPLEGABLE_SELECCIO = QComboBox()
        DESPLEGABLE_SELECCIO.addItem("* Selecciona un alumne *")
        DESPLEGABLE_SELECCIO.addItems(self.obtenir_llistat_alumnes_registrats())
        DESPLEGABLE_SELECCIO.setMaximumWidth(300)
        DISTRIBUCIO.addWidget(DESPLEGABLE_SELECCIO)

    def widget_informes(self):
        self.INFORME = QWidget()
        self.INFORME.resize(300, 300)
        DISTRIBUCIO = QVBoxLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.INFORME.setLayout(DISTRIBUCIO)

        GRUP_TIPUS = QGroupBox()
        GRUP_TIPUS.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        GRUP_TIPUS.setTitle("Tipus d'informe")
        GRUP_TIPUS.setFlat(True)
        GRUP_TIPUS_DISTRIBUCIO = QVBoxLayout()
        GRUP_TIPUS.setLayout(GRUP_TIPUS_DISTRIBUCIO)
        self.informe_seleccionat: Union[QButtonGroup, QButtonGroup] = QButtonGroup()
        opcio_escoltam = QRadioButton("Escolta'm")
        opcio_escoltam.setChecked(True)
        opcio_global = QRadioButton("Seguiment d'alumnes")
        self.informe_seleccionat.setExclusive(True)
        self.informe_seleccionat.addButton(opcio_escoltam, 0)
        self.informe_seleccionat.addButton(opcio_global, 1)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(opcio_escoltam)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(opcio_global)
        self.SELECTOR_ALUMNES = QComboBox()
        self.SELECTOR_ALUMNES.addItem("* Selecciona un alumne *")
        self.SELECTOR_ALUMNES.addItems("* Tots *")
        self.SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
        self.SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        DISTRIBUCIO.addWidget(GRUP_TIPUS)
        DISTRIBUCIO.addWidget(self.SELECTOR_ALUMNES)
        opcio_global.toggled.connect(self.seleccionar_informe)
        opcio_escoltam.toggled.connect(self.seleccionar_informe)

    def seleccionar_informe(self):

        if self.informe_seleccionat.checkedId() == 0:
            self.tipus_informes = 0
            self.SELECTOR_ALUMNES.setVisible(False)

        elif self.informe_seleccionat.checkedId() == 1:
            self.tipus_informes = 1
            self.SELECTOR_ALUMNES.setVisible(True)

    def mostrar_creacio(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.CREACIO)

    def mostrar_visualitzacio(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.VISUALITZAR_EDITAR)

    def mostrar_dates(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.DATES)

    def mostrar_informes(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.INFORME)

    def obtenir_llistat_alumnes(self):
        alumnes_entrada = self.cap.alumnat
        llistat_alumnes = []
        for alumne in alumnes_entrada:
            llistat_alumnes.append(alumne.nom)
        return llistat_alumnes

    def obtenir_llistat_alumnes_registrats(self):
        alumnes_entrada = self.cap.alumnat_registres
        llistat_alumnes = []
        for alumne in alumnes_entrada:
            llistat_alumnes.append(alumne.nom)
        return llistat_alumnes

    def obtenir_categories(self):
        categories_entrada = self.categoritzador.categories
        llistat_categories = []
        for categoria in categories_entrada:
            llistat_categories.append(categoria.nom)
        return llistat_categories

    def obtenir_llistat_registres(self):
        llista_registres = []
        if self.acces_registres.registres:
            for element in self.acces_registres.registres:
                registre_ind = [element.id, element.alumne, element.categoria, element.data, element.descripcio]
                llista_registres.append(registre_ind)
            return llista_registres
        else:
            return False


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
