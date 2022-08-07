from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QDate, QSize, QSortFilterProxyModel
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtWidgets import QGridLayout, QDateEdit, QPushButton, QLabel, QComboBox, QTextEdit, QHBoxLayout, \
    QVBoxLayout, QTableView, QAbstractItemView, QWizardPage, QWizard, QDialog, QMessageBox, QLineEdit, QFormLayout, \
    QDialogButtonBox
from src.agents.agents_gui import Calendaritzador, CapEstudis
from src.agents.formats import Alumne_comm, Alumne_nou, Data_gui_comm




class ModelEdicioAlumnes(QtCore.QAbstractTableModel):
    """Model de taula per a l'edicio d'alumnes"""

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole or role == Qt.UserRole:
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
        else:
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
            return 'Column {}'.format(section + 1)
        return super().headerData(section, orientation, role)


class Dialeg_afegir(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Afegir alumne")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None
        self.setupUI()

    def setupUI(self):
        self.nomcomplet = QLineEdit()
        self.nomcomplet.setObjectName("Nom complet")
        disposicio = QFormLayout()
        disposicio.addRow("Name:", self.nomcomplet)
        self.layout.addLayout(disposicio)
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = []
        if not self.nomcomplet.text():
            QMessageBox.critical(self, "Error!", f"You must provide a contact's {self.nomcomplet.objectName()}", )
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
        self.setText("Aquesta acció tambe esborrarà els\nregistres de l'alumne seleccionat. Estàs segur?")
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setButtonText(QMessageBox.Yes, "Si, esborrar")
        self.setIcon(QMessageBox.Warning)


class EditorDates(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.calendari_editor_dates = Calendaritzador()
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
        self.BOTO_DATES_DESAR = QPushButton(icon=QIcon("icones/document-save-symbolic.svg"), text="Desar")

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
            DATA_2N_FORMATQT = QDate.fromString(self.calendari_editor_dates.dates[0].dia, "dd/MM/yyyy")
            DATA_3ER_FORMATQT = QDate.fromString(self.calendari_editor_dates.dates[1].dia, "dd/MM/yyyy")
            self.DATA_SEGON_TRIMESTRE.setDate(DATA_2N_FORMATQT)
            self.DATA_TERCER_TRIMESTRE.setDate(DATA_3ER_FORMATQT)
        # Conectem amb la funcio per garantir resultats coherents:
        self.DATA_SEGON_TRIMESTRE.dateChanged.connect(self.coherencia_dates_trimestre)
        self.DATA_TERCER_TRIMESTRE.dateChanged.connect(self.coherencia_dates_trimestre)
        # Determinem els elements que apareixen al widget:
        DISTRIBUCIO.addWidget(ETIQUETA_SEGON, 0, 0)
        DISTRIBUCIO.addWidget(self.DATA_SEGON_TRIMESTRE, 0, 1)
        DISTRIBUCIO.addWidget(ETIQUETA_TERCER, 1, 0)
        DISTRIBUCIO.addWidget(self.DATA_TERCER_TRIMESTRE, 1, 1)
        DISTRIBUCIO.addWidget(self.BOTO_DATES_DESAR, 2, 0, 2, 0)

    def coherencia_dates_trimestre(self) -> object:
        """Funcio per garantir que la data del tercer trimestre sempre sigui, com a minim, un dia mes, que la del
        segon. """
        if self.DATA_SEGON_TRIMESTRE.date() >= self.DATA_TERCER_TRIMESTRE.date():
            data_3er = self.DATA_SEGON_TRIMESTRE.date().addDays(1)
            self.DATA_TERCER_TRIMESTRE.setDate(data_3er)
        elif self.DATA_TERCER_TRIMESTRE.date() <= self.DATA_SEGON_TRIMESTRE.date():
            data_2n = self.DATA_TERCER_TRIMESTRE.date().addDays(-1)
            self.DATA_SEGON_TRIMESTRE.setDate(data_2n)

    def modificacio_dates(self):
        data2n = self.DATA_SEGON_TRIMESTRE.date().toString('ISODate')
        data3er = self.DATA_TERCER_TRIMESTRE.date().toString('ISODate')
        data_original_2n = self.calendari_editor_dates.dates[0]
        data_original_3er = self.calendari_editor_dates.dates[1]
        missatge_actualitzacio = []
        if data_original_2n.dia != data2n:
            missatge_actualitzacio.append(Data_gui_comm(data_original_2n.id, data2n))
        if data_original_3er.dia != data3er:
            missatge_actualitzacio.append(Data_gui_comm(data_original_3er.id, data3er))


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
        self.SELECTOR_DATES.setDisplayFormat(u"dd/MM/yyyy")
        self.SELECTOR_DATES.setCalendarPopup(True)
        self.SELECTOR_DATES.setDate(QDate.currentDate())
        self.SELECTOR_DATES.setMaximumWidth(self.AMPLADA_DESPLEGABLES)
        ETIQUETA_DESCRIPCIO = QLabel("Descripcio: ")
        self.EDICIO_DESCRIPCIO = QTextEdit()

        self.BOTO_DESAR = QPushButton(icon=QIcon("icones/document-save-symbolic.svg"), text="Desar")
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
        self.dades_model_transformades = None
        self.dades_originals_transformades = None
        self.cap_edicio_alumnes = CapEstudis()
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
            self.TAULA_ALUMNES_MODEL = (ModelEdicioAlumnes([" "]))
            self.TAULA_ALUMNES.setModel(self.TAULA_ALUMNES_MODEL)
            self.TAULA_ALUMNES_MODEL.setHeaderData(2, Qt.Horizontal, "Alumne")
        else:
            self.TAULA_ALUMNES_MODEL = ModelEdicioAlumnes(dades_alumnes)
            self.TAULA_ALUMNES_MODEL.setHeaderData(2, Qt.Horizontal, "Alumne")
            self.TAULA_ALUMNES.setModel(self.TAULA_ALUMNES_MODEL)
            self.TAULA_ALUMNES.setColumnHidden(0, True)
            self.TAULA_ALUMNES.resizeColumnsToContents()
        # Creem els botons:
        self.BOTO_DESAR = QPushButton(icon=QIcon("icones/document-save-symbolic.svg"), text="Desar")
        self.BOTO_DESAR.setIconSize(QSize(24, 24))
        self.BOTO_AFEGIR = QPushButton(icon=QIcon("icones/value-increase-symbolic.svg"), text="Afegir")
        self.BOTO_AFEGIR.setIconSize(QSize(24, 24))
        self.BOTO_ELIMINAR = QPushButton(icon=QIcon("icones/edit-delete-symbolic.svg"), text="Eliminar")
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
                camp = dades_model.data(dades_model.index(fila, columna), Qt.DisplayRole)
                # Comprovem primer el numero de registre:
                if columna == 0:
                    # Si es un registre nou i no te id, l'afegim a la llista de nous registres:
                    if camp == "":
                        columna += 1
                        camp = dades_model.data(dades_model.index(fila, columna), Qt.DisplayRole)
                        nous_alumnes.append(Alumne_nou(camp))
                        fila += 1
                        continue
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
            resultat_afegir = self.cap_edicio_alumnes.afegir_alumnes(nous_alumnes)
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

        dialeg = Dialeg_afegir(self)
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
        self.setButtonLayout([QWizard.BackButton, QWizard.NextButton, QWizard.FinishButton, QWizard.CancelButton])
        self.setButtonText(QWizard.FinishButton, "Finalitzar")
        self.setButtonText(QWizard.BackButton, "Enrere")
        self.setButtonText(QWizard.CancelButton, "Cancel·lar")
        # Configuracio de la pagina inicial:
        self.PAGINAINICIAL_TEXT = QLabel("Aquesta aplicació serveix per a la gestió dels alumnes tutoritzats.\n"
                                         "S'ha detectat que no consten noms d'alumnes, registres previs ni dates de "
                                         "trimestre.\n "
                                         "A continuacio s'us demanara que introduiu aquestes dades.")
        self.PAGINAINICIAL_TEXT.setWordWrap(True)
        PAGINA_INICIAL_DISTRIBUCIO = QVBoxLayout()
        PAGINA_INICIAL_DISTRIBUCIO.addWidget(self.PAGINAINICIAL_TEXT)
        self.PAGINA_INICIAL = QWizardPage()
        self.PAGINA_INICIAL.setLayout(PAGINA_INICIAL_DISTRIBUCIO)
        self.pagina_alumnes = QWizardPage()
        self.PAGINA_INICIAL.setTitle("Inicialització")
        self.PAGINA_INICIAL.setSubTitle("Inicialització de l'aplicació")
        self.PAGINA_INICIAL.setPixmap(QWizard.WatermarkPixmap, QPixmap("icones/assistent.png"))
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

