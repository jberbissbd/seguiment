# -*- coding:utf-8 -*-
import datetime
import dateutil
import os
import sys
from typing import Union
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt, QDate, QSortFilterProxyModel, QLocale
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtWidgets import (QApplication, QComboBox, QToolBar, QTableView, QGridLayout, QMainWindow, QPushButton,
                               QStackedWidget, QButtonGroup,
                               QVBoxLayout, QWidget, QAbstractItemView, QSizePolicy, QRadioButton, QGroupBox,
                               QStatusBar, QStyleFactory, QStyledItemDelegate, QMessageBox)
from dateutil import parser
from agents_bbdd import AjudantDirectoris
from agents_gui import Comptable, Classificador, Calendaritzador, CapEstudis, CreadorInformes, Destructor \
    , Comprovador
from formats import Registres_gui_nou, Registresguicomm
from widgets import EditorDates, CreadorRegistres, EditorAlumnes, DialegSeleccioCarpeta


class DelegatDates(QStyledItemDelegate):
    """Delegat per a la columna de dates"""

    def __init__(self):
        super(DelegatDates, self).__init__()

    def displayText(self, value, locale) -> str:
        """Retorna el text que es mostra a la columna de dates"""
        if value != str(""):
            value = value.toPython()
            return value.strftime("%d/%m/%Y")


class SortFilterProxyModel(QSortFilterProxyModel):
    """Classe per a poder filtrar a la taula de la Finestra principal"""

    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}

    def setFilterByColumn(self, regex, column):
        """Filtrar per columna"""
        self.filters[column] = regex
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Funcio per a determinar si filtra per fila"""
        for key, regex in self.filters.items():
            ix = self.sourceModel().index(source_row, key, source_parent)
            if ix.isValid():
                text = self.sourceModel().data(ix).toString()
                if not text.contains(regex):
                    return False
        return True


class ModelVisualitzacio(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.noms = ["Alumne", "Categoria", "Data", "Descripció"]

    def data(self, index, role=Qt.DisplayRole):
        """Proporciona les dates del model"""
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole or role == Qt.UserRole:
                # See below for the nested-list data structure.
                # .row() indexes into the outer list,
                # .column() indexes into the sub-list
                value: object = self._data[index.row()][index.column()]
                if isinstance(value, datetime.date):
                    return QDate(value)
                return value

    def rowCount(self, index):
        """Recompte de files"""
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        """Proporciona el numero de columnes"""
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def flags(self, index):
        """Estableix les propietats de les cel·les segons la columna."""
        if 2 != index.column() or 1 != index.column():
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def setData(self, index, value, role):
        """Funcio per a guardar els canvis realitzats al model."""
        if role == Qt.EditRole | Qt.UserRole | Qt.EditRole and index.column() != 2 or index.column() != 1:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def headerData(self, section, orientation, role):
        """Retorna el nom de les capçaleres"""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.noms[section - 1]
            return section


class MainWindow(QMainWindow):
    """Classe per a la finestra principal"""
    senyal_alumnes_actualitzats = QtCore.Signal(bool)
    senyal_registres_actualitzats = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
        # Inicialització de la base de dades (es crea si no existeix)
        Comprovador(1)
        # Introduim la resta de parametres de la finestra principal
        self.INFORME = None
        self.selcarpeta = None
        self.SELECCIO_CARPETA = None
        self.BOTON_INFORME = None
        self.INFORMES_SELECTOR_CATEGORIES = None
        self.INFORMES_SELECTOR_ALUMNES = None
        self.TAULA_MODEL_FILTRE = None
        self.TAULA = None
        self.files_model = None
        self.columnes_model = None
        self.VISUALITZA_SELECCIO_CATEGORIES = None
        self.VISUALITZA_SELECCIO_ALUMNES = None
        self.BOTO_INFORMACIO = None
        self.BOTO_PURGAR = None
        self.BOTO_EDITAR_ALUMNES = None
        self.DATES = None
        self.destinacio_informes = None
        self.EDITAR_ALUMNES = None
        self.BARRA_NOTIFICACIONS = None
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
        self.BARRA_EINES_DISTRIBUCIO = None
        self.WIDGET_PRINCIPAL = None
        self.BOTO_VISUALITZAR = None
        self.crear_registres = None
        self.ruta_icones = AjudantDirectoris(1).ruta_icones
        self.cap = CapEstudis(modegui=1)
        self.categoritzador = Classificador(modegui=1)
        self.calendari = Calendaritzador(modegui=1)
        self.acces_registres = Comptable(modegui=1)
        self.info_alumnes = self.cap.info_alumnes
        self.configuracio_interficie()
        # Definim senyals:
        self.senyal_registres_actualitzats.connect(self.senyal_canvi_registres)
        self.senyal_alumnes_actualitzats.connect(self.senyal_canvi_alumnes)

    def configuracio_interficie(self):
        """Configuracio de la interficie"""
        self.setWindowTitle("Seguiment d'alumnes")
        self.resize(600, 500)
        # Configurem distribucio principal:
        # Configurem Widget principal:
        self.WIDGET_PRINCIPAL = QWidget()
        self.WIDGET_CENTRAL = QStackedWidget()
        # Creem i configurem la barra de notificacions:
        self.BARRA_NOTIFICACIONS = QStatusBar(self.WIDGET_PRINCIPAL)
        self.BARRA_NOTIFICACIONS.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.BARRA_NOTIFICACIONS.setStyle(QStyleFactory.create("Fusion"))
        self.BARRA_NOTIFICACIONS.setFixedHeight(20)
        self.BARRA_NOTIFICACIONS.setFixedWidth(20)
        self.BARRA_NOTIFICACIONS.setContentsMargins(0, 0, 0, 0)
        self.BARRA_NOTIFICACIONS.setVisible(True)
        self.BARRA_NOTIFICACIONS.setFont(QFont("Arial", 10))
        self.BARRA_NOTIFICACIONS.setEnabled(True)
        self.BARRA_NOTIFICACIONS.setSizeGripEnabled(True)
        self.setStatusBar(self.BARRA_NOTIFICACIONS)
        DISTRIBUCIO_PRINCIPAL = QVBoxLayout()
        DISTRIBUCIO_PRINCIPAL.setContentsMargins(5, 5, 5, 5)
        DISTRIBUCIO_PRINCIPAL.setSpacing(5)
        DISTRIBUCIO_PRINCIPAL.setAlignment(Qt.AlignTop)
        self.WIDGET_PRINCIPAL.setLayout(DISTRIBUCIO_PRINCIPAL)
        self.setCentralWidget(self.WIDGET_PRINCIPAL)
        self.widget_creacio()
        self.widget_edicio_alumnes()
        self.widget_visualitzacio()
        self.DATES = EditorDates()
        self.widget_informes()
        # Introduim la barra d'eines:
        self.BARRA_EINES_DISTRIBUCIO = QToolBar()
        self.BARRA_EINES_DISTRIBUCIO.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.BARRA_EINES_DISTRIBUCIO.setIconSize(QSize(32, 32))
        DISTRIBUCIO_PRINCIPAL.addWidget(self.BARRA_EINES_DISTRIBUCIO)
        DISTRIBUCIO_PRINCIPAL.addWidget(self.WIDGET_CENTRAL)
        DISTRIBUCIO_PRINCIPAL.addWidget(self.BARRA_NOTIFICACIONS)
        # Definim botons i les seves propietats:
        self.BOTO_CREAR = QAction(self, icon=QIcon(f"{self.ruta_icones}/edit-symbolic.svg"),
                                  text="Registrar")
        self.BOTO_CREAR.setToolTip("Crear un nou registre")
        self.BOTO_EDITAR_ALUMNES = QAction(self, icon=QIcon(f"{self.ruta_icones}/system-switch-user-symbolic.svg"),
                                           text="Alumnes")
        self.BOTO_EDITAR_ALUMNES.setToolTip("Editar les dades de l'alumne")
        self.BOTO_VISUALITZAR = QAction(self, icon=QIcon(f"{self.ruta_icones}/document-properties-symbolic.svg"),
                                        text="LListat")
        self.BOTO_VISUALITZAR.setToolTip("Visualitzar/Editar un registre")
        self.BOTO_DATES = QAction(self, icon=QIcon(f"{self.ruta_icones}/office-calendar-symbolic.svg"), text="Dates")
        self.BOTO_DATES.setToolTip("Dates trimestre")
        self.BOTO_INFORMES = QAction(self, icon=QIcon(f"{self.ruta_icones}/desar.svg"), text="Informes")
        self.BOTO_INFORMES.setToolTip("Informes")
        self.BOTO_SORTIR = QAction(self, icon=QIcon(f"{self.ruta_icones}/application-exit-symbolic.svg"), text="Sortir")
        self.BOTO_SORTIR.setToolTip("Sortir de l'aplicació")
        self.BOTO_INFORMACIO = QAction(self, icon=QIcon(f"{self.ruta_icones}/help-info-symbolic.svg"),
                                       text="Informació")
        self.BOTO_PURGAR = QAction(self, icon=QIcon(f"{self.ruta_icones}/mail-mark-junk-symbolic.svg"), text="Eliminar")
        # Afegim els botons a la barra d'eines:
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_CREAR)
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_VISUALITZAR)
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_EDITAR_ALUMNES)
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_DATES)
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_INFORMES)
        self.BARRA_EINES_DISTRIBUCIO.addSeparator()
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_SORTIR)
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_INFORMACIO)
        self.BARRA_EINES_DISTRIBUCIO.addSeparator()
        self.BARRA_EINES_DISTRIBUCIO.addAction(self.BOTO_PURGAR)
        # Afegim stack, un widget per cadascuna:
        self.WIDGET_CENTRAL.addWidget(self.CREACIO)
        self.WIDGET_CENTRAL.addWidget(self.VISUALITZAR_EDITAR)
        self.WIDGET_CENTRAL.addWidget(self.EDITAR_ALUMNES)
        self.WIDGET_CENTRAL.addWidget(self.DATES)
        self.WIDGET_CENTRAL.addWidget(self.INFORME)
        # Connectem botons:
        self.BOTO_CREAR.triggered.connect(self.mostrar_creacio)
        self.BOTO_VISUALITZAR.triggered.connect(self.mostrar_visualitzacio)
        self.BOTO_EDITAR_ALUMNES.triggered.connect(self.mostrar_editor_alumnes)
        self.BOTO_DATES.triggered.connect(self.mostrar_dates)
        self.BOTO_INFORMES.triggered.connect(self.mostrar_informes)
        self.BOTO_SORTIR.triggered.connect(sortir)
        self.BOTO_PURGAR.triggered.connect(self.eliminar_dades)

    def eliminar_dades(self):
        """Elimina les dades de la base de dades"""
        if QMessageBox.question(self, "Eliminar dades", "Estàs segur de que vols eliminar les dades?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            Destructor(1).destruir()
            sortir()

    def widget_creacio(self):
        """Configurem el widget de creacio de registres"""
        # Creem el widget de creacio de nous registres:
        self.CREACIO = CreadorRegistres()
        if self.obtenir_llistat_registres():
            self.CREACIO.SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes())
        self.CREACIO.SELECTOR_CATEGORIA.addItems(self.obtenir_categories())
        self.CREACIO.EDICIO_DESCRIPCIO.textChanged.connect(self.actualitzar_descripcio)
        self.CREACIO.BOTO_DESAR.clicked.connect(self.desar_registre)
        self.CREACIO.BOTO_DESAR.clicked.connect(self.senyal_registres_actualitzats)

    def widget_edicio_alumnes(self):
        """Configura el widget d'edicio d'alumnes."""
        if self.obtenir_llistat_alumnes():
            self.EDITAR_ALUMNES = EditorAlumnes(dades_alumnes=self.obtenir_registres_alumnes())
        else:
            self.EDITAR_ALUMNES = EditorAlumnes(dades_alumnes=[[]])
        self.EDITAR_ALUMNES.BOTO_DESAR.clicked.connect(self.senyal_alumnes_actualitzats)
        self.EDITAR_ALUMNES.BOTO_DESAR.clicked.connect(self.missatge_eliminats)

    def missatge_eliminats(self):
        """Emissio de notificacio de que s'han eliminat alumnes"""
        if self.EDITAR_ALUMNES.INDICADOR_ELIMINAT:
            self.statusBar().showMessage("Alumnes eliminats", 2000)

    def actualitzar_descripcio(self):
        """Bloqueja el boto desar si no hi ha descripcio."""
        if self.CREACIO.EDICIO_DESCRIPCIO.toPlainText() == "":
            self.CREACIO.BOTO_DESAR.setEnabled(False)
        self.CREACIO.BOTO_DESAR.setEnabled(True)

    def desar_registre(self):
        """Tracta els elements de la gui i transmet l'ordre de crear una nova entrada a la taula de registres"""
        # Desar un nou registre:
        alumne = self.CREACIO.SELECTOR_ALUMNES.currentText()
        categoria = self.CREACIO.SELECTOR_CATEGORIA.currentText()
        data = self.CREACIO.SELECTOR_DATES.date().toString("yyyy-MM-dd")
        descripcio = self.CREACIO.EDICIO_DESCRIPCIO.toPlainText()
        self.CREACIO.EDICIO_DESCRIPCIO.clear()
        missatge_creacio_output = []
        registre_individual = [alumne, categoria, data, descripcio]
        for persona in self.cap.alumnat:
            if persona.nom == registre_individual[0]:
                registre_individual[0] = persona
        for motiu in self.categoritzador.categories:
            if motiu.nom == registre_individual[1]:
                registre_individual[1] = motiu
        registre_individual = Registres_gui_nou(registre_individual[0], registre_individual[1], registre_individual[2],
                                                registre_individual[3])
        missatge_creacio_output.append(registre_individual)
        self.acces_registres.crear_registre(missatge_creacio_output)
        self.statusBar().showMessage("Registre desat correctament", 2000)

    def widget_visualitzacio(self):
        self.TAULA = QTableView()
        self.VISUALITZAR_EDITAR = QWidget()
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.VISUALITZAR_EDITAR.setLayout(DISTRIBUCIO)
        self.VISUALITZA_SELECCIO_ALUMNES = QComboBox()
        self.VISUALITZA_SELECCIO_CATEGORIES = QComboBox()
        self.VISUALITZA_SELECCIO_ALUMNES.addItem("* Filtrar per alumne *")
        self.VISUALITZA_SELECCIO_CATEGORIES.addItem("* Filtrar per categoria *")
        if self.obtenir_llistat_categories_registrades():
            self.VISUALITZA_SELECCIO_CATEGORIES.addItems(self.obtenir_llistat_categories_registrades())
        if self.obtenir_llistat_alumnes_registrats():
            self.VISUALITZA_SELECCIO_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
        self.VISUALITZA_SELECCIO_ALUMNES.setMaximumWidth(300)
        BOTO_DESAR = QPushButton(icon=QIcon(f"{self.ruta_icones}/desar.svg"), text="Desar canvis")
        BOTO_DESAR.clicked.connect(self.alteracio_registres)
        if self.obtenir_llistat_registres() not in [None, False]:
            self.TAULA_MODEL = ModelVisualitzacio(self.obtenir_llistat_registres())
            self.columnes_model: int = self.TAULA_MODEL.columnCount(1)
            self.files_model: int = self.TAULA_MODEL.rowCount(1)
        else:
            self.TAULA_MODEL = ModelVisualitzacio([[" ", " ", " ", " "]])
            self.columnes_model = 1
            self.files_model = 1
        noms_columnes = ["ID", "Alumne", "Motiu", "Data", "Descripció"]
        for nom in noms_columnes:
            self.TAULA_MODEL.setHeaderData(noms_columnes.index(nom), Qt.Horizontal, nom)
        # Poc elegant, pero el filtre funciona com a objecte intermig entre el model i la taula:
        self.TAULA_MODEL_FILTRE = QSortFilterProxyModel(self)
        self.TAULA_MODEL_FILTRE.setSourceModel(self.TAULA_MODEL)
        self.TAULA.setModel(self.TAULA_MODEL_FILTRE)
        # Establim el delegat per a la columna de dates:
        if self.obtenir_llistat_registres() not in [None, False]:
            self.TAULA.setItemDelegateForColumn(3, DelegatDates())
        # Possibilitat d'establir un ComboBox:
        # https://stackoverflow.com/questions/48105026/how-to-update-a-qtableview-cell-with-a-qcombobox-selection
        # Li indiquem que ha de filtrar de la columna 1:
        self.TAULA_MODEL_FILTRE.setFilterKeyColumn(-1)
        # I que hauria d'ordenar per la columna 3:
        self.TAULA_MODEL_FILTRE.sort(3, Qt.AscendingOrder)
        self.TAULA_MODEL_FILTRE.autoAcceptChildRows()
        self.TAULA_MODEL_FILTRE.setDynamicSortFilter(False)
        self.TAULA.setColumnHidden(0, True)
        self.TAULA.setWordWrap(True)
        self.TAULA.model().setHeaderData(1, Qt.Horizontal, "Alumne")
        self.TAULA.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.TAULA.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.TAULA.setSelectionMode(QAbstractItemView.SingleSelection)
        self.TAULA.setColumnWidth(4, self.AMPLADA_DESPLEGABLES)

        self.TAULA.resizeRowsToContents()
        self.TAULA.resizeColumnToContents(1)
        self.TAULA.resizeColumnToContents(2)
        self.TAULA.resizeColumnToContents(3)
        self.TAULA.setSortingEnabled(True)
        DISTRIBUCIO.addWidget(self.VISUALITZA_SELECCIO_ALUMNES, 0, 0)
        DISTRIBUCIO.addWidget(self.VISUALITZA_SELECCIO_CATEGORIES, 0, 1)
        DISTRIBUCIO.addWidget(BOTO_DESAR, 0, 2)
        DISTRIBUCIO.addWidget(self.TAULA, 1, 0, 1, 0)
        self.TAULA.doubleClicked.connect(self.bloqueig_registre_taula)
        self.VISUALITZA_SELECCIO_ALUMNES.currentTextChanged.connect(self.visualitzacio_filtre_alumnes)
        self.VISUALITZA_SELECCIO_CATEGORIES.currentTextChanged.connect(self.visualitzacio_filtre_categories)

    def visualitzacio_filtre_alumnes(self):
        """Comportament quan s'esta reallitzant un filtre per alumnes al widget amb el llistat"""
        valor_actual_desplegable = self.VISUALITZA_SELECCIO_ALUMNES.currentText()
        if self.VISUALITZA_SELECCIO_ALUMNES.currentIndex() == 0:
            self.TAULA.showColumn(1)
            self.VISUALITZA_SELECCIO_CATEGORIES.setCurrentIndex(0)
            self.TAULA_MODEL_FILTRE.setFilterWildcard("*")
            self.TAULA.resizeRowsToContents()
        self.VISUALITZA_SELECCIO_CATEGORIES.setCurrentIndex(0)
        self.TAULA_MODEL_FILTRE.invalidate()
        self.TAULA_MODEL_FILTRE.setFilterRegularExpression(valor_actual_desplegable)
        self.TAULA.hideColumn(1)
        self.TAULA.resizeRowsToContents()

    def visualitzacio_filtre_categories(self):
        categoria_seleccionada = self.VISUALITZA_SELECCIO_CATEGORIES.currentText()
        if self.VISUALITZA_SELECCIO_CATEGORIES.currentIndex() == 0:
            self.TAULA_MODEL_FILTRE.invalidate()
            self.TAULA_MODEL_FILTRE.setFilterWildcard("*")
            self.TAULA.resizeRowsToContents()
            self.TAULA.showColumn(1)
            self.VISUALITZA_SELECCIO_ALUMNES.setCurrentIndex(0)
        else:
            self.TAULA.showColumn(1)
            self.VISUALITZA_SELECCIO_ALUMNES.setCurrentIndex(0)
            self.TAULA_MODEL_FILTRE.invalidate()
            self.TAULA_MODEL_FILTRE.setFilterRegularExpression(categoria_seleccionada)
            self.TAULA.resizeRowsToContents()

    def senyal_canvi_registres(self):
        self.acces_registres.refrescar_registres()
        self.TAULA_MODEL = ModelVisualitzacio(self.obtenir_llistat_registres())
        self.TAULA.setModel(self.TAULA_MODEL)
        self.VISUALITZA_SELECCIO_ALUMNES.clear()
        self.VISUALITZA_SELECCIO_ALUMNES.addItem("* Filtrar per alumne *")
        self.cap.refrescar_alumnes()
        self.VISUALITZA_SELECCIO_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
        self.VISUALITZA_SELECCIO_CATEGORIES.clear()
        self.categoritzador.refrescar_categories_registres()
        self.VISUALITZA_SELECCIO_CATEGORIES.addItem("* Filtrar per categoria *")
        self.VISUALITZA_SELECCIO_CATEGORIES.addItems(self.obtenir_llistat_categories_registrades())

    def senyal_canvi_alumnes(self):
        """Actualitza els noms d'alumnes, i tambe els registres a visualitzar"""
        # Actualitzem els selectors d'alumnes:
        self.cap.refrescar_alumnes()
        self.obtenir_llistat_alumnes()
        self.CREACIO.SELECTOR_ALUMNES.clear()
        self.CREACIO.SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes())
        self.VISUALITZA_SELECCIO_ALUMNES.clear()
        self.VISUALITZA_SELECCIO_ALUMNES.addItem("* Selecciona un alumne *")
        self.VISUALITZA_SELECCIO_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
        # Actualitzem els registres, ja que la base de dades eliminara els registres d'un alumne.
        self.acces_registres.refrescar_registres()
        self.TAULA_MODEL = ModelVisualitzacio(self.obtenir_llistat_registres())
        self.TAULA.setModel(self.TAULA_MODEL)

    def bloqueig_registre_taula(self):
        # Editar un registre:
        index = self.TAULA.currentIndex()
        columna = index.column()
        if columna in (1, 2):
            self.statusBar().showMessage("No es pot editar aquest camp", 2000)
        self.TAULA.edit(index)

    def alteracio_registres(self):
        """Funcio per a comparar els registres de la taula quan hi ha canvis i gestionar-los, tant si s'eliminen com
        si s'afegien. """
        model_comparacio = self.TAULA.model()
        dades_originals = self.obtenir_llistat_registres()
        llista_ids_originals: list = [ref[0] for ref in dades_originals]
        llista_ids_model = []
        registres_eliminats: list = []
        registres_actualitzats: list = []
        rang_files = list(range(self.TAULA.model().rowCount()))
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
        # Transformem les dates de QT a python (per culpa de la taula de visualitzacio):
        for registre in llista_dades_model:
            registre[3] = registre[3].toString("yyyy-MM-dd")
        # Ordenem les dades del model per id:
        llista_dades_model.sort(key=lambda x: x[0])
        # Comparem els ids de les files del model amb els ids de les files originals:
        for item in rang_files:
            if llista_ids_originals[item] != llista_ids_model[item]:
                registres_eliminats.append(llista_ids_originals[item])
                item += 1

            # Un cop sapigut aixo, comprovem les actualitzacions:
            else:
                # Comprovem els registres un per un. Si son diferents, guardem els canvis:
                if dades_originals[item] != llista_dades_model[item]:
                    registres_actualitzats.append(llista_dades_model[item])

        # Comprovem si hi han actualitzacions o eliminacions i passem l'ordre corresponent:
        if registres_eliminats:
            self.eliminar_registres(registres_eliminats)
        if registres_actualitzats:
            self.actualitzar_registres(registres_actualitzats)

    def eliminar_registres(self, registres_eliminats):
        """Funcio per a eliminar registres de la base de dades."""
        missatge_eliminar = []
        for registre in registres_eliminats:
            eliminacio_registre = self.transformar_gui_a_bbdd(registre)
            missatge_eliminar.append(eliminacio_registre)
        self.acces_registres.eliminar_registre(missatge_eliminar)
        self.TAULA_MODEL.layoutChanged.emit()

    def actualitzar_registres(self, registres_actualitzats):
        """Funcio per a actualitzar registres de la base de dades."""
        missatge_actualitzacio = []
        for registre in registres_actualitzats:
            actualitzacio_registre = self.transformar_gui_a_bbdd(registre)
            missatge_actualitzacio.append(actualitzacio_registre)
        self.acces_registres.actualitzar_registres(missatge_actualitzacio)

    def transformar_gui_a_bbdd(self, dades: list):
        """Funcio per a transformar les dades de la GUI a la BBDD."""
        if not isinstance(dades, list):
            raise TypeError("La dada ha de ser del tipus Registresguicomm.")
        alumne = None
        categoria_enviar = None
        # Transformem la data:
        id_registre = dades[0]
        for persona in self.cap.alumnat:
            if persona.nom == dades[1]:
                alumne = persona
        for categoria in self.categoritzador.info_categories:
            if categoria.nom == dades[2]:
                categoria_enviar = categoria
        objecte_data = dateutil.parser.parse(dades[3], dayfirst=True)
        data = objecte_data.strftime("%Y-%m-%d")
        descripcio = dades[4]
        # Guardem la dada:
        resultat = Registresguicomm(id_registre, alumne, categoria_enviar, data, descripcio)
        return resultat

    def widget_informes(self):
        self.INFORME = QWidget()
        self.INFORME.resize(300, 300)
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.INFORME.setLayout(DISTRIBUCIO)
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
        opcio_categories = QRadioButton("Categories")
        opcio_categories.setChecked(False)
        opcio_alumnes = QRadioButton("Per alumne")
        self.informe_seleccionat.setExclusive(True)
        self.informe_seleccionat.addButton(opcio_categories, 0)
        self.informe_seleccionat.addButton(opcio_alumnes, 1)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(opcio_categories)
        GRUP_TIPUS_DISTRIBUCIO.addWidget(opcio_alumnes)
        # Creem les opcions per a l'exportacio o la importacio:
        self.tipus_accio_json = QButtonGroup()
        self.tipus_accio_json.setExclusive(True)
        opcio_exportar = QRadioButton("Exportar")

        opcio_importar = QRadioButton("Importar")
        self.tipus_accio_json.addButton(opcio_exportar, 0)
        self.tipus_accio_json.addButton(opcio_importar, 1)
        grup_export_importdistribucio.addWidget(opcio_exportar)
        grup_export_importdistribucio.addWidget(opcio_importar)
        # Creem el selector d'alumnes per a l'exportacio:
        self.exportimport_selector_alumnes = QComboBox()
        self.exportimport_selector_alumnes.addItem("* Tots *")
        self.exportimport_selector_alumnes.setVisible(False)

        # Creem els selectors d'informe en Excel:
        self.INFORMES_SELECTOR_ALUMNES = QComboBox()
        self.INFORMES_SELECTOR_ALUMNES.addItem("* Tots *")
        # Afegim les dades de la taula, si n'hi ha:
        if self.obtenir_llistat_alumnes_registrats():
            self.INFORMES_SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
            self.exportimport_selector_alumnes.addItems(self.obtenir_llistat_alumnes_registrats())
        self.INFORMES_SELECTOR_CATEGORIES = QComboBox()
        self.INFORMES_SELECTOR_CATEGORIES.addItem("* Totes *")
        if self.obtenir_llistat_categories_registrades():
            self.INFORMES_SELECTOR_CATEGORIES.addItems(self.obtenir_llistat_categories_registrades())
        self.INFORMES_SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.INFORMES_SELECTOR_ALUMNES.setVisible(False)
        self.INFORMES_SELECTOR_CATEGORIES.setVisible(False)
        self.INFORMES_SELECTOR_CATEGORIES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        # Creem els botons per a l'exportacio o importacio:
        self.export_seleccio_carpeta = QPushButton(QIcon(os.path.join(self.ruta_icones, "inode-directory-symbolic.svg")), "")
        self.export_seleccio_carpeta.setVisible(False)
        self.import_seleccio_arxiu = QPushButton(
            QIcon(os.path.join(self.ruta_icones, "inode-directory-symbolic.svg")), "Seleccioneu arxiu")
        self.import_seleccio_arxiu.setVisible(False)
        # Creem els botons per a la creacio d'informes en Excel:
        self.BOTON_INFORME = QPushButton("Generar informe")
        self.BOTON_INFORME.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.BOTON_INFORME.setVisible(False)
        self.SELECCIO_CARPETA = QPushButton(QIcon(os.path.join(self.ruta_icones, "inode-directory-symbolic.svg")), "")
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
        DISTRIBUCIO.addWidget(self.import_seleccio_arxiu, 3, 1)
        DISTRIBUCIO.addWidget(self.BOTON_INFORME, 4, 0)
        opcio_exportar.toggled.connect(self.seleccio_accio_json)
        opcio_alumnes.toggled.connect(self.seleccionar_informe)
        opcio_categories.toggled.connect(self.seleccionar_informe)
        self.BOTON_INFORME.clicked.connect(self.generar_informe)
        self.SELECCIO_CARPETA.clicked.connect(self.seleccionar_carpeta_informes)
        self.destinacio_informes = None
        self.carpeta_exportacio = None
        self.arxiu_importacio = None

    def seleccionar_carpeta_informes(self):
        """Funcio per a seleccionar la carpeta on es guardaran els informes."""
        self.selcarpeta = DialegSeleccioCarpeta().getExistingDirectory(self, "Selecciona carpeta")
        if self.selcarpeta:
            self.destinacio_informes = self.selcarpeta

    def exportar(self):
        pass

    def importar(self):
        pass

    def generar_informe(self):
        """Funcio per a generar un informe. Explicacio de la variable tipus informe: 0 si es de categories, 1 si es per
        alumne."""
        dades_registres = self.acces_registres.obtenir_registres()
        alumnes_informe = self.cap.alumnat_registres
        carpeta_desti = self.destinacio_informes
        categories_registrades = self.categoritzador.categories_registrades
        resposta = None
        if self.destinacio_informes is None:
            self.statusBar().showMessage("No s'ha seleccionat cap carpeta de destinacio.", 5000)
        else:
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
                dates_informe = self.calendari.info_dates
                valor_actual = self.INFORMES_SELECTOR_ALUMNES.currentText()
                categories_enviar = self.categoritzador.categories
                if self.INFORMES_SELECTOR_ALUMNES.currentIndex() != 0:
                    # Enviem tan sols la informacio de l'alumne en concret, no tot el registre:
                    alumnes_informe = [alumne for alumne in alumnes_informe if alumne.nom == valor_actual]
                    dades_enviar = [registre for registre in dades_registres if registre.alumne.nom == valor_actual]
                else:
                    dades_enviar = dades_registres
                exportador = CreadorInformes(alumnes_informe, categories_enviar, dades_enviar, carpeta_desti)
                resposta = exportador.export_alumne(dates_informe)
            if resposta:
                self.statusBar().showMessage("Informe generat correctament", 2000)

    def seleccio_accio_json(self):
        if self.tipus_accio_json.checkedId() == 0:
            self.exportimport_selector_alumnes.setVisible(True)
            self.export_seleccio_carpeta.setVisible(True)
            self.import_seleccio_arxiu.setVisible(False)
        else:
            self.exportimport_selector_alumnes.setVisible(False)
            self.export_seleccio_carpeta.setVisible(False)
            self.import_seleccio_arxiu.setVisible(True)

    def seleccionar_informe(self):
        self.BOTON_INFORME.setVisible(True)
        self.SELECCIO_CARPETA.setVisible(True)
        if self.informe_seleccionat.checkedId() == 0:
            self.tipus_informes = 0
            self.INFORMES_SELECTOR_CATEGORIES.setVisible(True)
            self.INFORMES_SELECTOR_ALUMNES.setVisible(False)
            self.INFORMES_SELECTOR_ALUMNES.setCurrentIndex(0)

        elif self.informe_seleccionat.checkedId() == 1:
            self.tipus_informes = 1
            self.INFORMES_SELECTOR_CATEGORIES.setVisible(False)
            self.INFORMES_SELECTOR_ALUMNES.setVisible(True)
            self.INFORMES_SELECTOR_CATEGORIES.setCurrentIndex(0)

    def mostrar_creacio(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.CREACIO)

    def mostrar_visualitzacio(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.VISUALITZAR_EDITAR)

    def mostrar_editor_alumnes(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.EDITAR_ALUMNES)

    def mostrar_dates(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.DATES)

    def mostrar_informes(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.INFORME)

    def obtenir_llistat_alumnes(self):
        alumnes_entrada = self.cap.alumnat
        if alumnes_entrada:
            llistat_alumnes = [alumne.nom for alumne in alumnes_entrada]

            return llistat_alumnes
        return False

    def obtenir_registres_alumnes(self):
        alumnes_entrada = self.cap.alumnat
        if alumnes_entrada:
            llistat_dades_alumnes = [[alumne.id, alumne.nom] for alumne in alumnes_entrada]
            return llistat_dades_alumnes
        return False

    def obtenir_llistat_alumnes_registrats(self):
        alumnes_entrada = self.cap.alumnat_registres
        if alumnes_entrada:
            llistat_alumnes = [alumne.nom for alumne in alumnes_entrada]
            return llistat_alumnes
        return False

    def obtenir_llistat_categories_registrades(self):
        categories_registre = self.categoritzador.obtenir_categories_registrades()
        if categories_registre:
            llistat_alumnes = [categoria.nom for categoria in categories_registre]
            return llistat_alumnes
        return False

    def obtenir_categories(self):
        categories_entrada = self.categoritzador.categories
        if categories_entrada:
            llistat_categories = [categoria.nom for categoria in categories_entrada]
            return llistat_categories
        return []

    def obtenir_llistat_registres(self):
        self.acces_registres.refrescar_registres()
        if self.acces_registres.registres:
            llista_registres = [[element.id, element.alumne.nom, element.categoria.nom,
                                 parser.parse(element.data), element.descripcio] for element
                                in self.acces_registres.registres]
            return llista_registres
        return None


def sortir():
    """Tanca l'aplicacio"""

    sys.exit(0)


app = QApplication(sys.argv)
QLocale.setDefault(QLocale.Catalan)
app.setStyle("Fusion")
window = MainWindow()
window.show()
sys.exit(app.exec())
