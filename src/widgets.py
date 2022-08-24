import os
from datetime import date
from typing import Union

import dateutil
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QDate, QSize, QLocale, QSortFilterProxyModel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QDateEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
    QWizardPage,
    QWizard,
    QDialog,
    QMessageBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QFileDialog, QGroupBox, QButtonGroup, QRadioButton, QStyledItemDelegate, QWidget,
)
from dateutil.parser import parser

from agents_bbdd import AjudantDirectoris
from agents_gui import Calendaritzador, CapEstudis, ExportadorImportador, CreadorInformes, Comptable, Classificador
from formats import Alumne_comm, AlumneNou, DataGuiComm, DataNova, Registresguicomm

QLocale.setDefault(QLocale.Catalan)


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
                if isinstance(value, date):
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


class DialegSeleccioCarpeta(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.Directory)


class ModelEdicioAlumnes(QtCore.QAbstractTableModel):
    """Model de taula per a l'edicio d'alumnes"""

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole):
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
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole or Qt.UserRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def add_row(self, dades):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(1), self.rowCount(1))
        self._data.append(dades[0])
        self.endInsertRows()

    def remove_row(self, row):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self._data.pop(row)
        self.endRemoveRows()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return "Column {}".format(section + 1)
        return super().headerData(section, orientation, role)


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
            DATA_2N_FORMATQT = QDate.fromString(
                self.calendari_editor_dates.dates[0].dia, "dd/MM/yyyy"
            )
            DATA_3ER_FORMATQT = QDate.fromString(
                self.calendari_editor_dates.dates[1].dia, "dd/MM/yyyy"
            )
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
        data2n = self.DATA_SEGON_TRIMESTRE.date().toString("ISODate")
        data3er = self.DATA_TERCER_TRIMESTRE.date().toString("ISODate")
        if self.calendari_editor_dates.dates:
            data_original_2n = self.calendari_editor_dates.dates[0]
            data_original_3er = self.calendari_editor_dates.dates[1]
            missatge_actualitzacio = []
            if data_original_2n.dia != data2n:
                missatge_actualitzacio.append(DataGuiComm(data_original_2n.id, data2n))
            if data_original_3er.dia != data3er:
                missatge_actualitzacio.append(
                    DataGuiComm(data_original_3er.id, data3er)
                )
            if len(missatge_actualitzacio) > 0:
                estat_actualitzacio = self.calendari_editor_dates.actualitza_dates(
                    missatge_actualitzacio
                )
        else:
            llista_noves_dates = [data2n, data3er]
            missatge_creacio = [DataNova(item) for item in llista_noves_dates]
            estat_creacio = Calendaritzador(1).registra_dates(missatge_creacio)
        return estat_actualitzacio + estat_creacio


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

        ETIQUETA_CATEGORIA = QLabel("Motiu:")
        ETIQUETA_CATEGORIA.setMaximumWidth(self.AMPLADA_ETIQUETES)
        self.SELECTOR_CATEGORIA = QComboBox()

        self.SELECTOR_CATEGORIA.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
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


class EditorAlumnes(QtWidgets.QWidget):
    def __init__(self, parent=None, dades_alumnes=None):
        self.confirmacio_eliminar = None
        self.dades_model_transformades = None
        self.dades_originals_transformades = None
        self.cap_edicio_alumnes = CapEstudis(1)
        QtWidgets.QWidget.__init__(self, parent)
        self.AMPLADA_ETIQUETES = 75
        self.AMPLADA_DESPLEGABLES = 200
        DISTRIBUCIO = QHBoxLayout()
        DISTRIBUCIO.setAlignment(Qt.AlignTop)
        self.setLayout(DISTRIBUCIO)
        self.TAULA_ALUMNES = QTableView()
        self.TAULA_ALUMNES.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.TAULA_ALUMNES.setSelectionMode(QAbstractItemView.SingleSelection)
        self.TAULA_ALUMNES.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.INDICADOR_ELIMINAT = None
        if not dades_alumnes:
            self.TAULA_ALUMNES_MODEL = ModelEdicioAlumnes([" "])
            self.TAULA_ALUMNES.setModel(self.TAULA_ALUMNES_MODEL)
            self.TAULA_ALUMNES_MODEL.setHeaderData(2, Qt.Horizontal, "Alumne")
        else:
            self.TAULA_ALUMNES_MODEL = ModelEdicioAlumnes(dades_alumnes)
            self.TAULA_ALUMNES_MODEL.setHeaderData(2, Qt.Horizontal, "Alumne")
            self.TAULA_ALUMNES.setModel(self.TAULA_ALUMNES_MODEL)
            self.TAULA_ALUMNES.setColumnHidden(0, True)
            self.TAULA_ALUMNES.resizeColumnsToContents()
        # Creem els botons:
        self.BOTO_DESAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/desar.svg"), text="Desar"
        )
        self.BOTO_DESAR.setIconSize(QSize(24, 24))
        self.BOTO_AFEGIR = QPushButton(
            icon=QIcon(
                f"{AjudantDirectoris(1).ruta_icones}/value-increase-symbolic.svg"
            ),
            text="Afegir",
        )
        self.BOTO_AFEGIR.setIconSize(QSize(24, 24))
        self.BOTO_ELIMINAR = QPushButton(
            icon=QIcon(f"{AjudantDirectoris(1).ruta_icones}/edit-delete-symbolic.svg"),
            text="Eliminar",
        )
        self.BOTO_ELIMINAR.setIconSize(QSize(24, 24))
        DISTRIBUCIO_BOTONS = QVBoxLayout()
        DISTRIBUCIO_BOTONS.setAlignment(Qt.AlignTop)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_AFEGIR)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_ELIMINAR)
        DISTRIBUCIO_BOTONS.addWidget(self.BOTO_DESAR)
        DISTRIBUCIO.addWidget(self.TAULA_ALUMNES)
        DISTRIBUCIO.addLayout(DISTRIBUCIO_BOTONS)
        # Connectem els botons:
        self.BOTO_AFEGIR.clicked.connect(self.afegir_alumne)
        self.BOTO_ELIMINAR.clicked.connect(self.eliminar_alumne)
        self.BOTO_DESAR.clicked.connect(self.alteracio_alumnes)
        self.TAULA_ALUMNES.doubleClicked.connect(self.modificar_alumne)

    def alteracio_alumnes(self):
        """Compara els registres d'alumnes de la gui i els originals, i els classifica per a modificar, eliminar o
        crear-ne un de nou, si correspon. I executa l'operacio corresponent a la base de dades"""
        # LLegim les dades de la base de dades:
        dades_originals = self.cap_edicio_alumnes.alumnat
        self.dades_originals_transformades = []
        llista_ids_originals = []
        llista_ids_model = []
        dades_model = self.TAULA_ALUMNES.model()
        rang_files = list(range(self.TAULA_ALUMNES.model().rowCount(1)))
        rang_columnes = list(range(self.TAULA_ALUMNES.model().columnCount(1)))
        self.dades_model_transformades = []
        nous_alumnes = []
        # Comprovem un per un els registres de la gui:
        for fila in rang_files:
            registre_model = []
            for columna in rang_columnes:
                camp = dades_model.data(
                    dades_model.index(fila, columna), Qt.DisplayRole
                )
                # Comprovem primer el numero de registre:
                if columna == 0:
                    # Si es un registre nou i no te id, l'afegim a la llista de nous registres:
                    if camp == "":
                        columna += 1
                        camp = dades_model.data(
                            dades_model.index(fila, columna), Qt.DisplayRole
                        )
                        nous_alumnes.append(AlumneNou(camp))
                        fila += 1
                    # Si te id, se l'afegeix a la llista de ID's per a comparar, i a les dades del model.
                    else:
                        llista_ids_model.append(camp)
                        registre_model.append(camp)
                else:
                    if camp is not None:
                        registre_model.append(camp)
                    # Confeccionem la llista d'ids del model:
            if registre_model:
                self.dades_model_transformades.append(registre_model)
        if len(dades_originals) != 0:
            for alumne in dades_originals:
                self.dades_originals_transformades.append([alumne.id, alumne.nom])
                # Afegim la llista d'ids originals:
                llista_ids_originals.append(alumne.id)
        # Ordenem la llista d'ids de les dades:
        llista_ids_originals.sort()
        llista_ids_model.sort()
        self.dades_originals_transformades.sort(key=lambda x: x[0])
        self.dades_model_transformades.sort(key=lambda x: x[0])
        # Comprovem si hi ha algun alumne modificat o a eliminar:
        alumnes_modificar = []
        missatge_eliminar = []
        # Fem comparacio de les llistes d'ids. Si estava a les dades inicials i no a les finals, es que s'ha marcat per
        # eliminar.
        alumnes_eliminar = list(set(llista_ids_originals).difference(llista_ids_model))
        # Comprovem els registres que queden al model de taula, per si s'han modificat.
        for registre in self.dades_model_transformades:
            if registre in self.dades_originals_transformades:
                continue
            else:
                alumnes_modificar.append(Alumne_comm([registre[0], registre[1]]))
        # Transformem els alumnes a eliminar a DTO:
        for alumne in dades_originals:
            if alumne.id in alumnes_eliminar:
                missatge_eliminar.append(Alumne_comm(alumne.id, alumne.nom))
        # Comprovem si hi ha algun alumne nou:
        if len(nous_alumnes) > 0:
            self.cap_edicio_alumnes.afegir_alumnes(nous_alumnes)
        if len(alumnes_modificar) > 0:
            self.cap_edicio_alumnes.actualitzar_alumnes(alumnes_modificar)
        if len(alumnes_eliminar) > 0:
            self.cap_edicio_alumnes.eliminar_alumnes(missatge_eliminar)
            # Modifiquem les dades que obte:
        self.cap_edicio_alumnes.refrescar_alumnes()
        info_alumnes = self.cap_edicio_alumnes.obtenir_alumnes()
        dades_actualitzades = [[persona.id, persona.nom] for persona in info_alumnes]
        self.TAULA_ALUMNES_MODEL = ModelEdicioAlumnes(dades_actualitzades)
        self.TAULA_ALUMNES.setModel(self.TAULA_ALUMNES_MODEL)

    def afegir_alumne(self):

        dialeg = DialegAfegir(self)
        if dialeg.exec() == QDialog.Accepted:
            self.TAULA_ALUMNES.model().add_row(dialeg.data)
            self.TAULA_ALUMNES.resizeColumnsToContents()

    def eliminar_alumne(self):
        self.confirmacio_eliminar = DialegEliminar()
        self.INDICADOR_ELIMINAT = self.confirmacio_eliminar.Yes
        if self.confirmacio_eliminar.exec() == QMessageBox.Yes:
            index = self.TAULA_ALUMNES.currentIndex()
            self.TAULA_ALUMNES_MODEL.remove_row(index.row())

    def modificar_alumne(self):
        # Editar un registre:
        index = self.TAULA_ALUMNES.currentIndex()
        self.TAULA_ALUMNES.edit(index)


class AssistentInicial(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistent d'inicialització")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(QSize(600, 400))
        self.setButtonLayout(
            [
                QWizard.BackButton,
                QWizard.NextButton,
                QWizard.FinishButton,
                QWizard.CancelButton,
            ]
        )
        self.setButtonText(QWizard.FinishButton, "Finalitzar")
        self.setButtonText(QWizard.BackButton, "Enrere")
        self.setButtonText(QWizard.CancelButton, "Cancel·lar")
        # Configuracio de la pagina inicial:
        self.PAGINAINICIAL_TEXT = QLabel(
            "Aquesta aplicació serveix per a la gestió dels alumnes tutoritzats.\n"
            "S'ha detectat que no consten noms d'alumnes, registres previs ni dates de "
            "trimestre.\n "
            "A continuacio s'us demanara que introduiu aquestes dades."
        )
        self.PAGINAINICIAL_TEXT.setWordWrap(True)
        PAGINA_INICIAL_DISTRIBUCIO = QVBoxLayout()
        PAGINA_INICIAL_DISTRIBUCIO.addWidget(self.PAGINAINICIAL_TEXT)
        self.PAGINA_INICIAL = QWizardPage()
        self.PAGINA_INICIAL.setLayout(PAGINA_INICIAL_DISTRIBUCIO)

        self.PAGINA_INICIAL.setTitle("Inicialització")
        self.PAGINA_INICIAL.setSubTitle("Inicialització de l'aplicació")
        self.PAGINA_INICIAL.setPixmap(
            QWizard.WatermarkPixmap,
            QPixmap(f"{AjudantDirectoris(1).ruta_icones}/assistent.png"),
        )
        # Configurem la pagina d'alumnes:
        self.PAGINA_ALUMNES = QWizardPage()
        self.PAGINA_ALUMNES.setTitle("Alumnes")
        PAGINA_ALUMNES_DISTRIBUCIO = QVBoxLayout()
        PAGINA_ALUMNES_DISTRIBUCIO.addWidget(EditorAlumnes())
        self.PAGINA_ALUMNES.setLayout(PAGINA_ALUMNES_DISTRIBUCIO)
        # Configurem la pagina de dates:
        self.PAGINA_DATES = QWizardPage()
        self.PAGINA_DATES.setTitle("Dates")
        PAGINA_DATES_DISTRIBUCIO = QVBoxLayout()
        PAGINA_DATES_DISTRIBUCIO.addWidget(EditorDates())
        self.PAGINA_DATES.setLayout(PAGINA_DATES_DISTRIBUCIO)
        self.PAGINA_DATES.setFinalPage(True)
        # Afegim les pagines:
        self.addPage(self.PAGINA_INICIAL)
        self.addPage(self.PAGINA_ALUMNES)
        self.addPage(self.PAGINA_DATES)


class GeneradorInformesExportImport(QtWidgets.QWidget):
    """Classe per a generar informes i exportar/importar"""

    def __init__(self):
        super().__init__()
        self.importacio = None
        self.selcarpeta = None
        self.tipus_informes = None
        self.desti_json = None
        self.resultat_exportacio = None
        self.resultat_informes = None
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
            QIcon(os.path.join(AjudantDirectoris(1).ruta_icones, "inode-directory-symbolic.svg")), "")
        self.boto_exportar_json = QPushButton("Exportar")
        self.boto_exportar_json.setVisible(False)
        self.export_seleccio_carpeta.setVisible(False)
        self.import_seleccio_arxiu = QPushButton(
            QIcon(os.path.join(AjudantDirectoris(1).ruta_icones, "inode-directory-symbolic.svg")), "Seleccioneu arxiu")
        self.import_seleccio_arxiu.setVisible(False)
        # Creem els botons per a la creacio d'informes en Excel:
        self.BOTON_INFORME = QPushButton("Generar informe")
        self.BOTON_INFORME.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        self.BOTON_INFORME.setVisible(False)
        self.SELECCIO_CARPETA = QPushButton(QIcon(os.path.join(AjudantDirectoris(1).ruta_icones,
                                                               "inode-directory-symbolic.svg")), "")
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
        self.desti_json = DialegSeleccioCarpeta().getExistingDirectory(self, "Selecciona carpeta")
        if self.desti_json:
            self.carpeta_exportacio = self.desti_json

    def seleccionar_carpeta_informes(self):
        """Funcio per a seleccionar la carpeta on es guardaran els informes."""
        self.selcarpeta = DialegSeleccioCarpeta().getExistingDirectory(self, "Selecciona carpeta")
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
        self.importacio = DialegSeleccioCarpeta().getOpenFileNames(self, "Selecciona carpeta", filter="Arxius json("
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


def obtenir_llistat_alumnes():
    alumnes_entrada = CapEstudis(1).alumnat
    if alumnes_entrada:
        llistat_alumnes = [alumne.nom for alumne in alumnes_entrada]
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
                             dateutil.parser.parse(element.data), element.descripcio] for element
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


class EditorRegistres(QtWidgets.QWidget):
    def __init__(self):
        super(EditorRegistres, self).__init__()
        self.AMPLADA_DESPLEGABLES = 200
        self.TAULA = QTableView()
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
        if obtenir_llistat_registres() not in [None, False]:
            self.TAULA_MODEL = ModelVisualitzacio(obtenir_llistat_registres())
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
        if obtenir_llistat_registres() not in [None, False]:
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
        DISTRIBUCIO.addWidget(self.seleccio_alumnes, 0, 0)
        DISTRIBUCIO.addWidget(self.seleccio_categories, 0, 1)
        DISTRIBUCIO.addWidget(self.boto_desar, 0, 2)
        DISTRIBUCIO.addWidget(self.TAULA, 1, 0, 1, 0)
        self.seleccio_alumnes.currentTextChanged.connect(self.visualitzacio_filtre_alumnes)
        self.seleccio_categories.currentTextChanged.connect(self.visualitzacio_filtre_categories)
        self.boto_desar.clicked.connect(self.alteracio_registres)

    def alteracio_registres(self):
        """Funcio per a comparar els registres de la taula quan hi ha canvis i gestionar-los, tant si s'eliminen com
        si s'afegien. """
        model_comparacio = self.TAULA.model()
        dades_originals = obtenir_llistat_registres()
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
            raise TypeError("La dada ha de ser del tipus Registresguicomm.")
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
        objecte_data = dateutil.parser.parse(dades[3], dayfirst=True)
        data = objecte_data.strftime("%Y-%m-%d")
        descripcio = dades[4]
        # Guardem la dada:
        resultat = Registresguicomm(id_registre, alumne, categoria_enviar, data, descripcio)
        return resultat

    def visualitzacio_filtre_alumnes(self):
        """Comportament quan s'esta reallitzant un filtre per alumnes al widget amb el llistat"""
        valor_actual_desplegable = self.seleccio_alumnes.currentText()
        self.seleccio_categories.setCurrentIndex(0)
        if self.seleccio_alumnes.currentIndex() == 0:
            self.TAULA.showColumn(1)
            self.seleccio_categories.setCurrentIndex(0)
            self.TAULA_MODEL_FILTRE.setFilterWildcard("*")
            self.TAULA.resizeRowsToContents()
        else:
            self.TAULA_MODEL_FILTRE.invalidate()
            self.TAULA_MODEL_FILTRE.setFilterRegularExpression(valor_actual_desplegable)
            self.TAULA.hideColumn(1)
            self.TAULA.resizeRowsToContents()

    def visualitzacio_filtre_categories(self):
        categoria_seleccionada = self.seleccio_categories.currentText()
        if self.seleccio_categories.currentIndex() == 0:
            self.TAULA_MODEL_FILTRE.invalidate()
            self.TAULA_MODEL_FILTRE.setFilterWildcard("*")
            self.TAULA.resizeRowsToContents()
            self.TAULA.showColumn(1)
            self.seleccio_alumnes.setCurrentIndex(0)
        else:
            self.TAULA.showColumn(1)
            self.seleccio_alumnes.setCurrentIndex(0)
            self.TAULA_MODEL_FILTRE.invalidate()
            self.TAULA_MODEL_FILTRE.setFilterRegularExpression(categoria_seleccionada)
            self.TAULA.resizeRowsToContents()
