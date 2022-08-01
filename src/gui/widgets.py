from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtWidgets import QGridLayout, QDateEdit, QPushButton, QLabel, QComboBox, QTextEdit, QHBoxLayout, \
    QVBoxLayout, QTableView, QAbstractItemView, QWizardPage, QWizard
from src.agents.agents_gui import Calendaritzador, CapEstudis
from src.agents.formats import Alumne_comm, Alumne_nou


class ModelEdicioAlumnes(QtCore.QAbstractTableModel):
    """Model de taula per a l'edicio d'alumnes"""

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
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole | Qt.UserRole | Qt.EditRole and index.column() or index.column() != 1:
            self._data[index.row()][index.column()] = value
            return True
        else:
            return False

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Column {}'.format(section + 1)
        return super().headerData(section, orientation, role)


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
        if dades_alumnes is None:
            self.TAULA_ALUMNES.setModel(ModelEdicioAlumnes([[]]))
        else:
            self.TAULA_ALUMNES.setModel(ModelEdicioAlumnes(dades_alumnes))
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
        self.BOTO_AFEGIR.clicked.connect(self.alteracio_alumnes)
        self.BOTO_ELIMINAR.clicked.connect(self.eliminar_alumne)
        self.BOTO_DESAR.clicked.connect(self.alteracio_alumnes)

    def alteracio_alumnes(self):
        # LLegim les dades de la base de dades:
        dades_originals = self.cap_edicio_alumnes.alumnat
        self.dades_originals_transformades = []
        llista_ids_originals = []
        llista_ids_model = []
        dades_model = self.TAULA_ALUMNES.model()
        rang_files = list(range(self.TAULA_ALUMNES.model().rowCount(1)))
        rang_columnes = list(range(self.TAULA_ALUMNES.model().columnCount(1)))
        self.dades_model_transformades = []
        for fila in rang_files:
            registre_model = []
            for columna in rang_columnes:
                camp = dades_model.data(dades_model.index(fila, columna), Qt.DisplayRole)
                # Confeccionem la llista d'ids del model:
                if columna == 0:
                    llista_ids_model.append(camp)
                registre_model.append(camp)
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
        # Comprovem si hi ha algun alumne nou:
        nous_alumnes = []
        alumnes_modificar = []
        alumnes_eliminar = []
        missatge_eliminar = []
        # Comprovem els nous registres d'alumnes:
        for registre in self.dades_model_transformades:
            # Si no hi ha registre, es un nou alumne:
            if registre[0] == "":
                nous_alumnes.append(Alumne_nou([1]))
            # Si hi ha id (registre[0]), es un alumne que ja existia, i comprovem si s'ha modificat:
            else:
                # Si el id no existeix a la llista d'ids originals, s'ha marcat per a eliminar:
                if registre[0] not in llista_ids_originals:
                    alumnes_eliminar.append(Alumne_nou([1]))
                # Si el id existeix a la llista d'ids originals, comprovem si s'ha modificat:
                else:
                    # L'afegim a la llista de modificacions:
                    if registre in self.dades_originals_transformades:
                        continue
                    else:
                        alumnes_modificar.append(Alumne_comm([registre[0], registre[1]]))
        # Comprovem els alumnes que s'han d'eliminar:
        for alumne in dades_originals:
            if alumne.id in alumnes_eliminar:
                missatge_eliminar.append(Alumne_comm([alumne.id, alumne.nom]))
        # Comprovem si hi ha algun alumne nou:
        if len(nous_alumnes) > 0:
            self.cap_edicio_alumnes.afegir_alumnes(nous_alumnes)
        if len(alumnes_modificar) > 0:
            self.cap_edicio_alumnes.actualitzar_alumnes(alumnes_modificar)

    def afegir_alumne(self):
        print("Afegir alumne")

    def eliminar_alumne(self):
        print("Eliminar alumne")

    def modificar_alumne(self):
        print("Modificar alumne")

class AssistentInicial(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistent d'inicialització")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(QSize(600, 400))
        self.setButtonLayout([QWizard.BackButton, QWizard.NextButton, QWizard.FinishButton, QWizard.CancelButton])

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
        self.PAGINA_ALUMNES = QWizardPage()
        self.PAGINA_ALUMNES.setTitle("Alumnes")
        PAGINA_ALUMNES_DISTRIBUCIO = QVBoxLayout()
        PAGINA_ALUMNES_DISTRIBUCIO.addWidget(EditorAlumnes())
        self.PAGINA_ALUMNES.setLayout(PAGINA_ALUMNES_DISTRIBUCIO)
        self.setButtonText(QWizard.FinishButton, "Finalitzar")
        self.setButtonText(QWizard.BackButton, "Enrere")
        self.setButtonText(QWizard.CancelButton, "Cancel·lar")
        # Afegim les pagines:
        self.addPage(self.PAGINA_INICIAL)
        self.addPage(self.PAGINA_ALUMNES)
