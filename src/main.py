# -*- coding:utf-8 -*-
import sys
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt, QLocale
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtWidgets import (QApplication, QToolBar, QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
                               QSizePolicy, QStatusBar,
                               QStyleFactory, QMessageBox)
from agents_bbdd import AjudantDirectoris
from agents_gui import Comptable, Classificador, Calendaritzador, CapEstudis, Destructor, Comprovador
from formats import Registres_gui_nou
from widgets import EditorDates, CreadorRegistres, EditorAlumnes, GeneradorInformesExportImport, EditorRegistres, \
    obtenir_registres_alumnes, ModelVisualitzacio, obtenir_llistat_registres, obtenir_llistat_alumnes_registrats, \
    obtenir_llistat_categories_registrades, obtenir_llistat_alumnes, obtenir_categories, EditorRegistresBis


class MainWindow(QMainWindow):
    """Classe per a la finestra principal"""
    senyal_alumnes_actualitzats = QtCore.Signal(bool)
    senyal_registres_actualitzats = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
        # Inicialització de la base de dades (es crea si no existeix)
        Comprovador(1)
        # Introduim la resta de parametres de la finestra principal
        self.informes_exportador = None
        self.files_model = None
        self.columnes_model = None
        self.boto_informacio = None
        self.boto_purgar = None
        self.boto_editor_alumnes = None
        self.editor_dates = None
        self.editor_alumnes = None
        self.notificador = None
        self.boto_dates = None
        self.boto_informes = None
        self.visualitzador = None
        self.creacio = None
        self.boto_creacio_registres = None
        self.widget_central = None
        self.boto_sortir = None
        self.barra_superior = None
        self.widget_principal = None
        self.boto_visualitzador = None
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
        self.widget_principal = QWidget()
        self.widget_central = QStackedWidget()
        # Creem i configurem la barra de notificacions:
        self.notificador = QStatusBar(self.widget_principal)
        self.notificador.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.notificador.setStyle(QStyleFactory.create("Fusion"))
        self.notificador.setFixedHeight(20)
        self.notificador.setFixedWidth(20)
        self.notificador.setContentsMargins(0, 0, 0, 0)
        self.notificador.setVisible(True)
        self.notificador.setFont(QFont("Arial", 10))
        self.notificador.setEnabled(True)
        self.notificador.setSizeGripEnabled(True)
        self.setStatusBar(self.notificador)
        distribucio_principal = QVBoxLayout()
        distribucio_principal.setContentsMargins(5, 5, 5, 5)
        distribucio_principal.setSpacing(5)
        distribucio_principal.setAlignment(Qt.AlignTop)
        self.widget_principal.setLayout(distribucio_principal)
        self.setCentralWidget(self.widget_principal)
        self.widget_creacio()
        self.widget_edicio_alumnes()
        self.widget_visualitzacio()
        self.editor_dates = EditorDates()
        self.widget_informes()
        # Introduim la barra d'eines:
        self.barra_superior = QToolBar()
        self.barra_superior.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.barra_superior.setIconSize(QSize(32, 32))
        distribucio_principal.addWidget(self.barra_superior)
        distribucio_principal.addWidget(self.widget_central)
        distribucio_principal.addWidget(self.notificador)
        # Definim botons i les seves propietats:
        self.boto_creacio_registres = QAction(self, icon=QIcon(f"{self.ruta_icones}/edit-symbolic.svg"),
                                              text="Registrar")
        self.boto_creacio_registres.setToolTip("Crear un nou registre")
        self.boto_editor_alumnes = QAction(self, icon=QIcon(f"{self.ruta_icones}/system-switch-user-symbolic.svg"),
                                           text="Alumnes")
        self.boto_editor_alumnes.setToolTip("Editar les dades de l'alumne")
        self.boto_visualitzador = QAction(self, icon=QIcon(f"{self.ruta_icones}/document-properties-symbolic.svg"),
                                          text="LListat")
        self.boto_visualitzador.setToolTip("Visualitzar/Editar un registre")
        self.boto_dates = QAction(self, icon=QIcon(f"{self.ruta_icones}/office-calendar-symbolic.svg"), text="Dates")
        self.boto_dates.setToolTip("Dates trimestre")
        self.boto_informes = QAction(self, icon=QIcon(f"{self.ruta_icones}/desar.svg"), text="Informes")
        self.boto_informes.setToolTip("Informes")
        self.boto_sortir = QAction(self, icon=QIcon(f"{self.ruta_icones}/application-exit-symbolic.svg"), text="Sortir")
        self.boto_sortir.setToolTip("Sortir de l'aplicació")
        self.boto_informacio = QAction(self, icon=QIcon(f"{self.ruta_icones}/help-info-symbolic.svg"),
                                       text="Informació")
        self.boto_purgar = QAction(self, icon=QIcon(f"{self.ruta_icones}/mail-mark-junk-symbolic.svg"), text="Eliminar")
        # Afegim els botons a la barra d'eines:
        self.barra_superior.addAction(self.boto_creacio_registres)
        self.barra_superior.addAction(self.boto_visualitzador)
        self.barra_superior.addAction(self.boto_editor_alumnes)
        self.barra_superior.addAction(self.boto_dates)
        self.barra_superior.addAction(self.boto_informes)
        self.barra_superior.addSeparator()
        self.barra_superior.addAction(self.boto_sortir)
        self.barra_superior.addAction(self.boto_informacio)
        self.barra_superior.addSeparator()
        self.barra_superior.addAction(self.boto_purgar)
        # Afegim stack, un widget per cadascuna:
        self.widget_central.addWidget(self.creacio)
        self.widget_central.addWidget(self.visualitzador)
        self.widget_central.addWidget(self.editor_alumnes)
        self.widget_central.addWidget(self.editor_dates)
        self.widget_central.addWidget(self.informes_exportador)
        # Connectem botons:
        self.boto_creacio_registres.triggered.connect(self.mostrar_creacio)
        self.boto_visualitzador.triggered.connect(self.mostrar_visualitzacio)
        self.boto_editor_alumnes.triggered.connect(self.mostrar_editor_alumnes)
        self.boto_dates.triggered.connect(self.mostrar_dates)
        self.boto_informes.triggered.connect(self.mostrar_informes)
        self.boto_sortir.triggered.connect(sortir)
        self.boto_purgar.triggered.connect(self.eliminar_dades)

    def eliminar_dades(self):
        """Elimina les dades de la base de dades"""
        if QMessageBox.question(self, "Eliminar dades", "Estàs segur de que vols eliminar les dades?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            Destructor(1).destruir()
            sortir()

    def widget_creacio(self):
        """Configurem el widget de creacio de registres"""
        # Creem el widget de creacio de nous registres:
        self.creacio = CreadorRegistres()
        if obtenir_llistat_registres():
            self.creacio.SELECTOR_ALUMNES.addItems(obtenir_llistat_alumnes())
        self.creacio.SELECTOR_CATEGORIA.addItems(obtenir_categories())
        self.creacio.EDICIO_DESCRIPCIO.textChanged.connect(self.actualitzar_descripcio)
        self.creacio.BOTO_DESAR.clicked.connect(self.desar_registre)
        self.creacio.BOTO_DESAR.clicked.connect(self.senyal_registres_actualitzats)

    def widget_edicio_alumnes(self):
        """Configura el widget d'edicio d'alumnes."""
        if obtenir_llistat_alumnes():
            self.editor_alumnes = EditorAlumnes(dades_alumnes=obtenir_registres_alumnes())
        else:
            self.editor_alumnes = EditorAlumnes(dades_alumnes=[[]])
        self.editor_alumnes.BOTO_DESAR.clicked.connect(self.senyal_alumnes_actualitzats)
        self.editor_alumnes.BOTO_DESAR.clicked.connect(self.missatge_eliminats)

    def missatge_eliminats(self):
        """Emissio de notificacio de que s'han eliminat alumnes"""
        if self.editor_alumnes.INDICADOR_ELIMINAT:
            self.statusBar().showMessage("Alumnes eliminats", 2000)

    def actualitzar_descripcio(self):
        """Bloqueja el boto desar si no hi ha descripcio."""
        if self.creacio.EDICIO_DESCRIPCIO.toPlainText() == "":
            self.creacio.BOTO_DESAR.setEnabled(False)
        self.creacio.BOTO_DESAR.setEnabled(True)

    def desar_registre(self):
        """Tracta els elements de la gui i transmet l'ordre de crear una nova entrada a la taula de registres"""
        # Desar un nou registre:
        alumne = self.creacio.SELECTOR_ALUMNES.currentText()
        categoria = self.creacio.SELECTOR_CATEGORIA.currentText()
        data = self.creacio.SELECTOR_DATES.date().toString("yyyy-MM-dd")
        descripcio = self.creacio.EDICIO_DESCRIPCIO.toPlainText()
        self.creacio.EDICIO_DESCRIPCIO.clear()
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
        """Funcio per a que es mostri el widget per a visualitzar i editar els registres"""
        self.visualitzador = EditorRegistresBis()
        self.visualitzador.boto_desar.clicked.connect(self.senyal_registres_actualitzats)
        # self.visualitzador.TAULA.doubleClicked.connect(self.bloqueig_registre_taula)

    def senyal_canvi_registres(self):
        """Funcio per a que s'actualitzin els regitres a la gui quan aquests es modifiquen"""
        self.acces_registres.refrescar_registres()
        self.visualitzador.TAULA_MODEL = ModelVisualitzacio(obtenir_llistat_registres())
        self.visualitzador.TAULA.setModel(self.visualitzador.TAULA_MODEL)
        self.visualitzador.seleccio_alumnes.clear()
        self.visualitzador.seleccio_alumnes.addItem("* Filtrar per alumne *")
        self.cap.refrescar_alumnes()
        self.visualitzador.seleccio_alumnes.addItems(obtenir_llistat_alumnes_registrats())
        self.visualitzador.seleccio_categories.clear()
        self.categoritzador.refrescar_categories_registres()
        self.visualitzador.seleccio_categories.addItem("* Filtrar per categoria *")
        self.visualitzador.seleccio_categories.addItems(obtenir_llistat_categories_registrades())

    def senyal_canvi_alumnes(self):
        """Actualitza els noms d'alumnes, i tambe els registres a visualitzar"""
        # Actualitzem els selectors d'alumnes:
        self.cap.refrescar_alumnes()
        self.creacio.SELECTOR_ALUMNES.clear()
        self.creacio.SELECTOR_ALUMNES.addItems(obtenir_llistat_alumnes())
        self.visualitzador.seleccio_alumnes.clear()
        self.visualitzador.seleccio_alumnes.addItem("* Selecciona un alumne *")
        self.visualitzador.seleccio_alumnes.addItems(obtenir_llistat_alumnes_registrats())
        # Actualitzem els registres, ja que la base de dades eliminara els registres d'un alumne.
        self.acces_registres.refrescar_registres()
        self.visualitzador.TAULA_MODEL = ModelVisualitzacio(obtenir_llistat_registres())
        self.visualitzador.TAULA.setModel(self.visualitzador.TAULA_MODEL)

    def bloqueig_registre_taula(self):
        """Bloqueja els camps categoria i alumne al widget de visualitzacio"""
        # Editar un registre:
        index = self.visualitzador.TAULA.currentIndex()
        columna = index.column()
        if columna in (1, 2):
            self.statusBar().showMessage("No es pot editar aquest camp", 2000)
        self.visualitzador.TAULA.edit(index)

    def widget_informes(self):
        """Configura el widget d'informes"""
        self.informes_exportador = GeneradorInformesExportImport()
        # Afegim les dades de la taula, si n'hi ha:
        if obtenir_llistat_alumnes_registrats():
            self.informes_exportador.INFORMES_SELECTOR_ALUMNES.addItems(obtenir_llistat_alumnes_registrats())
            self.informes_exportador.exportimport_selector_alumnes.addItems(obtenir_llistat_alumnes_registrats())
        if obtenir_llistat_categories_registrades():
            self.informes_exportador.INFORMES_SELECTOR_CATEGORIES.addItems(obtenir_llistat_categories_registrades())
        self.informes_exportador.boto_exportar_json.clicked.connect(self.missatges_exportacio)
        self.informes_exportador.BOTON_INFORME.clicked.connect(self.missatges_informe)

    def missatges_informe(self):
        """Configura el missatge a mostrar en el moment d'exportar els informes"""
        if self.informes_exportador.resultat_informes:
            self.statusBar().showMessage("Informe generat correctament", 2000)
        elif self.informes_exportador.destinacio_informes is None:
            self.statusBar().showMessage("No s'ha seleccionat cap carpeta de destinacio.", 5000)

    def missatges_exportacio(self):
        """Configura el missatge a mostrar per a l'exportacio a format json"""
        if self.informes_exportador.resultat_exportacio is True:
            self.statusBar().showMessage("Exportacio finalitzada", 2000)
        elif self.informes_exportador.resultat_exportacio is False:
            self.statusBar().showMessage("Error en l'exportacio", 2000)
        elif self.informes_exportador.resultat_exportacio == "nocarpeta":
            self.statusBar().showMessage("No s'ha seleccionat cap carpeta", 2000)

    def mostrar_creacio(self):
        """Mostra el widget de creacio de registres"""
        self.widget_central.setCurrentWidget(self.creacio)

    def mostrar_visualitzacio(self):
        """Mostra el widget de visualitzacio i edicio de registres"""
        self.widget_central.setCurrentWidget(self.visualitzador)

    def mostrar_editor_alumnes(self):
        """Mostra el widget d'edicio d'alumnes"""
        self.widget_central.setCurrentWidget(self.editor_alumnes)

    def mostrar_dates(self):
        """Mostra el widget d'edicio de dates"""
        self.widget_central.setCurrentWidget(self.editor_dates)

    def mostrar_informes(self):
        """Mostra el widget de creacio d'informes i per a exporta i importar en format json"""
        self.widget_central.setCurrentWidget(self.informes_exportador)


def sortir():
    """Tanca l'aplicacio"""

    sys.exit(0)


app = QApplication(sys.argv)
QLocale.setDefault(QLocale.Catalan)
app.setStyle("Fusion")
window = MainWindow()
window.show()
sys.exit(app.exec())
