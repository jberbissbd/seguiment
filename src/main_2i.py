import datetime
import sys
from dataclasses import dataclass
from typing import Union

import dateutil.parser

from src.agents.formats import Registres_gui_nou, Registres_gui_comm, Registres_bbdd_comm
from src.agents.agents_gui import Comptable, Classificador, Calendaritzador, CapEstudis
from dateutil import parser
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt, QDate
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit,
                               QToolBar, QTableView, QGridLayout, QLabel,
                               QMainWindow, QPushButton, QStackedWidget, QButtonGroup,
                               QTextEdit, QVBoxLayout, QWidget, QAbstractItemView, QSizePolicy, QRadioButton, QGroupBox,
                               QStatusBar,
                               QStyleFactory, QWizard)
from src.gui.widgets import EditorDates, CreadorRegistres, EditorAlumnes, AssistentInicial


def sortir():
    app.quit()


class ModelVisualitzacio(QtCore.QAbstractTableModel):
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
        if 2 != index.column() or 1 != index.column():
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if role == Qt.EditRole | Qt.UserRole | Qt.EditRole and index.column() != 2 or index.column() != 1:
            self._data[index.row()][index.column()] = value
            return True
        else:
            return False

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Column {}'.format(section + 1)
        return super().headerData(section, orientation, role)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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
        self.cap = CapEstudis()
        self.categoritzador = Classificador()
        self.calendari = Calendaritzador()
        self.acces_registres = Comptable()
        self.info_alumnes = self.cap.info_alumnes
        self.configuracio_interficie()

    def configuracio_interficie(self):
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
        self.widget_visualitzacio()
        self.DATES = EditorDates()
        self.EDITAR_ALUMNES = EditorAlumnes(dades_alumnes=self.obtenir_registres_alumnes())
        self.widget_informes()
        # Introduim la barra d'eines:
        self.BARRA_EINES_DISTRIBUCIO = QToolBar()
        self.BARRA_EINES_DISTRIBUCIO.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.BARRA_EINES_DISTRIBUCIO.setIconSize(QSize(32, 32))
        DISTRIBUCIO_PRINCIPAL.addWidget(self.BARRA_EINES_DISTRIBUCIO)
        DISTRIBUCIO_PRINCIPAL.addWidget(self.WIDGET_CENTRAL)
        DISTRIBUCIO_PRINCIPAL.addWidget(self.BARRA_NOTIFICACIONS)
        # Definim botons i les seves propietats:
        self.BOTO_CREAR = QAction(self, icon=QIcon("icones/edit-symbolic.svg"), text="Registrar")
        self.BOTO_CREAR.setToolTip("Crear un nou registre")
        self.BOTO_EDITAR_ALUMNES = QAction(self, icon=QIcon("icones/system-switch-user-symbolic.svg"), text="Alumnes")
        self.BOTO_EDITAR_ALUMNES.setToolTip("Editar les dades de l'alumne")
        self.BOTO_VISUALITZAR = QAction(self, icon=QIcon("icones/document-properties-symbolic.svg"),
                                            text="LListat")
        self.BOTO_VISUALITZAR.setToolTip("Visualitzar/Editar un registre")
        self.BOTO_DATES = QAction(self, icon=QIcon("icones/office-calendar-symbolic.svg"), text="Dates")
        self.BOTO_DATES.setToolTip("Dates trimestre")
        self.BOTO_INFORMES = QAction(self, icon=QIcon("icones/document-save-symbolic.svg"), text="Informes")
        self.BOTO_INFORMES.setToolTip("Informes")
        self.BOTO_SORTIR = QAction(self, icon=QIcon("icones/application-exit-symbolic.svg"), text="Sortir")
        self.BOTO_SORTIR.setToolTip("Sortir de l'aplicació")
        self.BOTO_INFORMACIO = QAction(self, icon=QIcon("icones/help-info-symbolic.svg"), text="Informació")
        self.BOTO_PURGAR = QAction(self, icon=QIcon("icones/mail-mark-junk-symbolic.svg"), text="Eliminar")
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

    def widget_creacio(self):
        # Creem el widget de creacio de nous registres:
        self.CREACIO = CreadorRegistres()
        self.CREACIO.SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes())
        self.CREACIO.SELECTOR_CATEGORIA.addItems(self.obtenir_categories())
        self.CREACIO.EDICIO_DESCRIPCIO.textChanged.connect(self.actualitzar_descripcio)
        self.CREACIO.BOTO_DESAR.clicked.connect(self.desar_registre)

    def actualitzar_descripcio(self):
        if self.CREACIO.EDICIO_DESCRIPCIO.toPlainText() == "":

            self.CREACIO.BOTO_DESAR.setEnabled(False)
        else:
            self.CREACIO.BOTO_DESAR.setEnabled(True)

    def desar_registre(self):
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
        self.VISUALITZAR_EDITAR = QWidget()
        DISTRIBUCIO = QGridLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.VISUALITZAR_EDITAR.setLayout(DISTRIBUCIO)
        DESPLEGABLE_SELECCIO = QComboBox()
        DESPLEGABLE_SELECCIO.addItem("* Selecciona un alumne *")
        DESPLEGABLE_SELECCIO.addItems(self.obtenir_llistat_alumnes_registrats())
        DESPLEGABLE_SELECCIO.setMaximumWidth(300)
        BOTO_DESAR = QPushButton(icon=QIcon("icones/document-save-symbolic.svg"), text="Desar canvis")
        BOTO_DESAR.clicked.connect(self.alteracio_registres)
        self.TAULA_MODEL = ModelVisualitzacio(self.obtenir_llistat_registres())
        noms_columnes = ["ID", "Alumne", "Motiu", "Data", "Descripció"]
        for nom in noms_columnes:
            self.TAULA_MODEL.setHeaderData(noms_columnes.index(nom), Qt.Horizontal, nom)

        self.columnes_model: int = self.TAULA_MODEL.columnCount(1)
        self.files_model: int = self.TAULA_MODEL.rowCount(1)
        self.TAULA = QTableView()
        self.TAULA.setModel(self.TAULA_MODEL)
        self.TAULA.setColumnHidden(0, True)
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
        DISTRIBUCIO.addWidget(DESPLEGABLE_SELECCIO, 0, 0)
        DISTRIBUCIO.addWidget(BOTO_DESAR, 0, 1)
        DISTRIBUCIO.addWidget(self.TAULA, 1, 0, 1, 0)
        self.TAULA.doubleClicked.connect(self.bloqueig_registre_taula)

    def bloqueig_registre_taula(self):
        # Editar un registre:
        index = self.TAULA.currentIndex()
        columna = index.column()
        if columna == 1 or columna == 2:
            self.statusBar().showMessage("No es pot editar aquest camp", 2000)
        else:
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
            raise TypeError("La dada ha de ser del tipus Registres_gui_comm.")
        else:
            id_registre = None
            alumne = None
            categoria_enviar = None
            data = None
            descripcio = None
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
            resultat = Registres_gui_comm(id_registre, alumne, categoria_enviar, data, descripcio)
            return resultat

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
        self.SELECTOR_ALUMNES.addItem("* Tots *")
        self.SELECTOR_ALUMNES.addItems(self.obtenir_llistat_alumnes_registrats())
        self.SELECTOR_ALUMNES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.SELECTOR_ALUMNES.setVisible(False)
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

    def mostrar_editor_alumnes(self):
        self.WIDGET_CENTRAL.setCurrentWidget(self.EDITAR_ALUMNES)

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

    def obtenir_registres_alumnes(self):
        alumnes_entrada = self.cap.alumnat
        llistat_dades_alumnes = []
        for alumne in alumnes_entrada:
            llistat_dades_alumnes.append([alumne.id, alumne.nom])
        return llistat_dades_alumnes

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
                data_formatada = parser.parse(element.data).strftime("%d/%m/%Y")
                registre_ind = [element.id, element.alumne.nom, element.categoria.nom, data_formatada,
                                element.descripcio]

                llista_registres.append(registre_ind)
            return llista_registres
        else:
            return False


app = QApplication(sys.argv)

window = MainWindow()
a = AssistentInicial()
window.show()
a.show()


sys.exit(app.exec())
