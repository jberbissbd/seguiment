import sys
from datetime import date, timedelta
from typing import List, Any

import PySide6.QtCore
import PySide6.QtGui
from PySide6.QtCore import QSize, Qt, QAbstractTableModel, QDate
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                               QFileDialog, QToolBar, QTableView, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget, QAbstractItemView, QWizard, QWizardPage, QDialog)

from funcions import (Escriptor, Lector, Iniciador, Exportador)

# TODO: Reestructurar segons https://realpython.com/pyinstaller-python/

literal_alumnes = "Alumne: "


class MissatgeInfor(QWidget):
    def __init__(self):
        super().__init__()
        self.dialeginfo = QWidget()
        self.setWindowTitle("Llicencies")
        self.resize(300, 200)
        self.setMinimumWidth(300)
        self.dialeg_info_dist = QGridLayout()
        self.dialeg_info_dist.setAlignment(Qt.AlignTop)
        self.setLayout(self.dialeg_info_dist)
        self.nom_llicencia = QLabel("Programa per a fer el\nseguiment de l'alumnat.\nLlicencia: ")
        self.nom_llicencia.setWordWrap(True)
        self.link_llicencia = QLabel("<a href='https://www.gnu.org/licenses/gpl-3.0.ca.html'>GPLv3</a>")
        self.nom_autor = QLabel("Jordi Berbis")
        self.correu = QLabel("<a href='mailto:jberbis@xtec.cat'>jberbis@xtec.cat</a> ")
        self.correu.setOpenExternalLinks(True)
        self.text_icones = QLabel("Icones (GPLv3):")
        self.url_icones = QLabel(
            "<a href='https://github.com/PapirusDevelopmentTeam/papirus-icon-theme/'>Papirus Icon Theme</a>")
        self.url_icones.setOpenExternalLinks(True)
        self.url_icones.setTextFormat(Qt.RichText)
        self.icones_llicencia = "Papirus icon theme"
        self.dialeg_info_dist.addWidget(self.nom_llicencia, 0, 0)
        self.dialeg_info_dist.addWidget(self.link_llicencia, 0, 1, Qt.AlignBottom)
        self.dialeg_info_dist.addWidget(self.nom_autor)
        self.dialeg_info_dist.addWidget(self.correu)
        self.dialeg_info_dist.addWidget(self.text_icones)
        self.dialeg_info_dist.addWidget(self.url_icones)


class MainWindow(QMainWindow):
    alumnes_registrats: List[Any]

    def __init__(self):
        super().__init__()
        self.avui = PySide6.QtCore.QDate.currentDate()
        self.fin = Exportacio()
        self.editor = DadesAlumnes()
        self.editor_dates = DatesTrimestre()
        self.sobre = MissatgeInfor()
        self.bot_dist = QHBoxLayout()
        self.regbot = QPushButton("Registrar")
        self.tbot = QGridLayout()
        self.form_dist = QFormLayout()
        self.disp_general = QVBoxLayout()
        self.selector_data = QDateEdit(self.avui)
        self.desplegable_cat = QComboBox()
        self.categories_etiqueta = QLabel("Motiu: ")
        self.barra_eines = QToolBar(self)
        self.wcentral = QWidget()
        self.menu = self.menuBar()
        self.arxiu_menu = self.menu.addMenu("&Fitxer")
        self.sobre_accio = QAction(text="Sobre")
        self.purga_accio = QAction(self, icon=QIcon("src/icones/mail-mark-junk-symbolic.svg"))
        self.sortir_accio_text = QAction(self, icon=QIcon("src/icones/system-shutdown-symbolic.svg"), text="Sortir")
        self.sortir_accio = QAction(self, icon=QIcon("src/icones/system-shutdown-symbolic.svg"))
        self.exportar_accio = QAction(self, icon=QIcon("src/icones/application-exit-symbolic.svg"))
        self.edicio_dates = None
        self.editar_alumnes = None
        self.avui = PySide6.QtCore.QDate.currentDate()
        self.data_etiqueta = QLabel("Data:")
        self.qdesc = QTextEdit()
        self.qdesc_et = QLabel("Descripció:")
        self.desplegable_al = None
        self.alumnes_etiqueta = None
        self.arrencador = Iniciador()
        self.consultor = Lector()
        self.registrador = Escriptor()
        self.arrencador.creadortaules()
        self.al_registre: str = ""
        self.cat_registre: str = ""
        self.data_registre: str = date.isoformat(date.today())
        self.configurar_interficie()
        if self.arrencador.comprovadorinicicurs():
            self.asi = AssistentInicial()
            self.asi.show()

    def configurar_interficie(self):
        self.setWindowTitle("Seguiment alumnes")
        self.setFixedSize(PySide6.QtCore.QSize(300, 400))
        # Definim accions:
        self.editar_alumnes = QAction(self, icon=QIcon("src/icones/system-switch-user-symbolic.svg"))
        self.editar_alumnes.setToolTip("Editar alumnes")
        self.edicio_dates = QAction(self, icon=QIcon("src/icones/office-calendar-symbolic.svg"))
        self.edicio_dates.setToolTip("Editar dates de trimestre")
        self.exportar_accio.setToolTip("Exportar informes")
        self.sortir_accio.setToolTip("Sortir del programa")
        # Configurem menu:
        self.menu.setNativeMenuBar(False)
        self.menu.setFont(PySide6.QtGui.QFont("Arial", 10))
        self.arxiu_menu.addAction(self.sortir_accio_text)
        self.sortir_accio_text.triggered.connect(self.sortir)
        self.menu.addAction(self.sobre_accio)
        self.sobre_accio.triggered.connect(self.llicencia)
        # Configurem bloc d'alumnes:
        self.alumnes_etiqueta = QLabel(literal_alumnes)
        self.setCentralWidget(self.wcentral)
        self.desplegable_al = QComboBox()
        self.desplegable_al.addItems(self.consultor.llista_alumnes_desplegable())
        self.al_registre = self.desplegable_al.currentText()
        self.desplegable_al.currentTextChanged.connect(self.traspas_alumnes)
        # Configurem barra d'eines:
        self.barra_eines.setFloatable(False)
        self.barra_eines.setMovable(False)
        self.addToolBar(self.barra_eines)
        self.purga_accio.setToolTip("Eliminar registres")
        self.barra_eines.addAction(self.editar_alumnes)
        self.barra_eines.addAction(self.edicio_dates)
        self.barra_eines.addAction(self.exportar_accio)
        self.barra_eines.addAction(self.sortir_accio)
        self.barra_eines.addSeparator()
        self.barra_eines.addAction(self.purga_accio)
        self.barra_eines.setIconSize(QSize(32, 32))
        self.editar_alumnes.triggered.connect(self.edicio_alumnes)
        self.edicio_dates.triggered.connect(self.editar_dates)
        self.sortir_accio.triggered.connect(self.sortir)
        self.exportar_accio.triggered.connect(self.crear_informes)
        self.purga_accio.triggered.connect(self.purga_registres)
        # Configurem bloc de motius:
        self.desplegable_cat.addItems(self.consultor.llista_categories())
        self.cat_registre = self.desplegable_cat.currentText()
        self.desplegable_cat.currentTextChanged.connect(self.traspas_categoria)
        # Configurem bloc de descripció:
        self.qdesc_et.setFixedSize(100, 30)
        # Afegim data
        self.selector_data.setDisplayFormat(u"dd/MM/yyyy")
        self.selector_data.setCalendarPopup(True)
        self.selector_data.dateChanged.connect(self.traspas_data)
        # Configurem part formulari:
        self.form_dist.setVerticalSpacing(0)
        self.form_dist.setHorizontalSpacing(0)
        self.form_dist.setContentsMargins(1, 1, 1, 1)
        self.form_dist.addRow(self.alumnes_etiqueta, self.desplegable_al)
        self.form_dist.addRow(self.categories_etiqueta, self.desplegable_cat)
        self.form_dist.addRow(self.data_etiqueta, self.selector_data)
        self.form_dist.addRow(self.qdesc_et, self.qdesc)

        # Configurem text i botons:
        self.regbot.clicked.connect(self.registrar)
        self.bot_dist.addWidget(self.regbot)
        self.tbot.addLayout(self.bot_dist, 1, 0, 1, 2)
        # Configuració final de la part general:
        self.disp_general.addLayout(self.form_dist)
        self.disp_general.addLayout(self.tbot)
        self.wcentral.setLayout(self.disp_general)

    @staticmethod
    def sortir():
        app.quit()

    def llicencia(self):
        self.sobre.show()

    def registrar(self):
        descripcio = self.qdesc.toPlainText()
        if descripcio == "":
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Registre buit")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No s'ha proporcionat cap descripció")
            dlg.exec()
        else:
            self.registrador.registre_dades(self.al_registre, self.cat_registre, self.data_registre, descripcio)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Registre introduït")
            dlg.exec()
            self.qdesc.clear()

    def crear_informes(self):
        """Comprova si hi ha registres previs i activa el diàleg d'exportació si n'hi han"""
        dades = self.consultor.llista_alumnes_registres()
        if not dades:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Sense dades")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No existeix cap alumne amb registres")
            dlg.exec()

        else:
            self.alumnes_registrats = dades
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

    def edicio_alumnes(self):
        """Permet editar els alumnes en seguiment"""
        self.editor.show()

    def editar_dates(self):
        """Permet modificar les dates dels trimestres"""
        self.editor_dates.show()

    def purga_registres(self):
        """Permet eliminar registres"""
        dialeg_purga = QMessageBox(self)
        dialeg_purga.addButton("Si", QMessageBox.ApplyRole)
        dialeg_purga.addButton("No", QMessageBox.RejectRole)
        dialeg_purga.setIcon(QMessageBox.Critical)
        dialeg_purga.setWindowTitle("ATENCIO")
        dialeg_purga.setText("Voleu eliminar els registres?")
        dialeg_purga.show()
        resultat = dialeg_purga.exec()
        if resultat == 0:
            self.registrador.eliminar_registres()
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Registres purgats")
            dlg.exec()
            app.quit()
        elif resultat == 1:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Cancel·lat")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Purga cancel·lada")
            dlg.exec()

class DialegSeleccioCarpeta(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.Directory)


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class DadesAlumnes(QWidget):
    def __init__(self):
        super().__init__()
        self.distribucio = QGridLayout()
        self.distribucio_botons = QVBoxLayout()
        self.tornarBoto = QPushButton(icon=QIcon("src/icones/draw-arrow-back.svg"), text="Tornar")
        self.esborrarBoto = QPushButton("Esborrar")
        self.afegirBoto = QPushButton("Afegir")
        self.model = None
        self.alumnes = None
        self.taula_alumnes = None
        self.consultor_alumnes = Lector()
        self.configinterficie()

    def configinterficie(self):
        self.setWindowTitle("Alumnes")
        self.resize(300, 200)
        # Configurem la taula:
        self.taula_alumnes = QTableView()
        self.alumnes = self.consultor_alumnes.llista_alumnes()
        self.model = TableModel(self.alumnes)
        self.taula_alumnes.setModel(self.model)
        self.taula_alumnes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.taula_alumnes.resizeColumnsToContents()
        # Configurem els botons:
        self.distribucio_botons.addWidget(self.afegirBoto)
        self.distribucio_botons.addWidget(self.esborrarBoto)
        self.distribucio_botons.addWidget(self.tornarBoto)
        self.distribucio_botons.setAlignment(Qt.AlignTop)
        self.distribucio_botons.setSpacing(10)
        # Especifiquem les opcions de cada boto:
        self.tornarBoto.clicked.connect(self.retornar)
        # Configurem la interficie:
        self.distribucio.addWidget(self.taula_alumnes, 0, 0)
        self.distribucio.addLayout(self.distribucio_botons, 0, 1)
        self.distribucio.setAlignment(Qt.AlignTop)
        self.setLayout(self.distribucio)

    def retornar(self):
        DadesAlumnes.close(self)


class DatesTrimestre(QWidget):
    def __init__(self):
        super().__init__()
        self.consultor_dates = Lector()
        self.registradodates = Escriptor()
        self.dist_gen = QVBoxLayout()
        self.dist_boto = QHBoxLayout()
        self.distform = QFormLayout()
        self.data2ntrimestre = QDate.fromString(self.consultor_dates.llista_dates()[0], Qt.DateFormat.ISODate)
        self.data3rtrimestre = QDate.fromString(self.consultor_dates.llista_dates()[1], Qt.DateFormat.ISODate)
        self.desarBoto = QPushButton(icon=QIcon("src/icones/document-save-symbolic.svg"), text="Desar")
        self.tornarBoto = QPushButton(icon=QIcon("src/icones/draw-arrow-back.svg"), text="Tornar")
        self.etiq3rtrim = QLabel("Inici tercer trimestre:")
        self.editdata3rtrim = QDateEdit(self.data3rtrimestre)
        self.etiq2ntrim = QLabel("Inici 2n trimestre:")
        self.editdata2ntrim = QDateEdit(self.data2ntrimestre)
        # A continuacio llegim les dates de la BBDD i la passem a format QT, especificant que estan en format ISO:
        self.avui = PySide6.QtCore.QDate.currentDate()
        self.dema = self.avui.addDays(1)
        self.trimconfiginterficie()

    def trimconfiginterficie(self):
        # Establim parametres generals de la finestra:
        self.setWindowTitle("Trimestre")
        self.resize(300, 100)
        # Definim els elements que formaran part de la finestra:
        self.editdata2ntrim.setDisplayFormat(u"dd/MM/yyyy")
        self.editdata2ntrim.setCalendarPopup(True)
        self.editdata3rtrim.setDisplayFormat(u"dd/MM/yyyy")
        self.editdata3rtrim.setCalendarPopup(True)
        # Explicitem les funcions dels botons i dels controls:
        self.tornarBoto.clicked.connect(self.retornar)
        self.editdata2ntrim.dateChanged.connect(self.data2ntrim)
        self.editdata3rtrim.dateChanged.connect(self.data3ertrim)
        self.desarBoto.clicked.connect(self.desar)
        # Definim la distribucio:
        self.distform.addRow(self.etiq2ntrim, self.editdata2ntrim)
        self.distform.addRow(self.etiq3rtrim, self.editdata3rtrim)
        self.dist_boto.addWidget(self.tornarBoto)
        self.dist_boto.addWidget(self.desarBoto)
        self.dist_gen.setSpacing(10)
        self.dist_gen.setAlignment(Qt.AlignTop)
        self.dist_gen.addLayout(self.distform)
        self.dist_gen.addLayout(self.dist_boto)
        self.setLayout(self.dist_gen)

    def retornar(self):
        DatesTrimestre.close(self)

    def desar(self):
        data2n = self.data2ntrimestre
        data3r = self.data3rtrimestre
        self.registradodates.actualitzacio_dates(data2n, data3r)

    def data2ntrim(self):
        """Comprova la data del segon trimestre i la reajusta perquè com a minim
                sigui un dia menys que la del segon trimestre.
                """

        if self.editdata2ntrim.date() < self.editdata3rtrim.date():
            data_qt2n = self.editdata2ntrim.date()
            self.data2ntrimestre = data_qt2n.toPython()
            data_qt3r = self.editdata3rtrim.date()
            self.data3rtrimestre = data_qt3r.toPython()
        else:
            canvi3ertrim = self.editdata2ntrim.date()
            canvi3ertrim = canvi3ertrim.addDays(1)
            self.editdata3rtrim.setDate(canvi3ertrim)
            self.data2ntrimestre = self.editdata2ntrim.date()
            self.data3rtrimestre = canvi3ertrim.toPython()

    def data3ertrim(self):
        """Comprova la data del tercer trimestre i la reajusta per a que com a minim
        sigui un dia mes que la del segon trimestre.
        """

        if self.editdata2ntrim.date() < self.editdata3rtrim.date():
            data_qt2n = self.editdata2ntrim.date()
            self.data2ntrimestre = data_qt2n.toPython()
            data_qt3r = self.editdata3rtrim.date()
            self.data3rtrimestre = data_qt3r.toPython()
        else:
            canvi2ntrim = self.editdata3rtrim.date().toPython()
            canvi2ntrim = canvi2ntrim - timedelta(1)
            self.editdata2ntrim.setDate(canvi2ntrim)
            self.data3rtrimestre = self.editdata3rtrim.date().toPython()
            self.data2ntrimestre = canvi2ntrim


class FinestraExport(QWidget):
    def __init__(self):
        super().__init__()
        self.consultor_exportar = Lector()
        self.informador = Exportador()
        self.al_seleccionat: str = ''
        self.carpeta_desti: str = ''
        self.arxiu_desti: str = ''
        self.alumnes_registrats = self.consultor_exportar.llista_alumnes_registres()
        # Creació dels elements de la finestra:
        self.disposicio = QGridLayout()
        self.disposicio.setColumnStretch(2, 2)
        self.setWindowTitle("Creació d'informe")
        self.resize(300, 100)
        self.alumne_etiqueta = QLabel(literal_alumnes)
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
        self.boto_ok.clicked.connect(self.informador.export_escolta_m)
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
        sel.setFileMode(QFileDialog.AnyFile)
        sel.setNameFilter("Excel (*.xlsx)")
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
                self.consultor_exportar.export_global(alumne)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Informes exportats")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                dlg.close()
                self.close()

        elif self.tots_check.isChecked() is False:
            self.informador.export_informes_seguiment(self.al_seleccionat)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Èxit")
            dlg.setIcon(QMessageBox.Information)
            dlg.setText("Informes exportats")
            boto = dlg.exec()
            if boto == QMessageBox.Ok:
                dlg.close()
                self.close()

        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Sense dades")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("No existeix cap alumne amb registres")
            dlg.exec()


class Exportacio(QWidget):
    def __init__(self):
        super().__init__()
        self.carpeta_seleccionada = None
        self.consultor_export = Lector()
        self.dialeg = DialegSeleccioCarpeta()
        self.al_seleccionat: str = ''
        self.exportador_informes = Exportador()
        self.setWindowTitle("Creació d'informe")
        self.resize(300, 100)
        self.exportacio_disposicio = QGridLayout()
        self.setLayout(self.exportacio_disposicio)
        self.seleccio_tipus_informe = QLabel("Selecciona un informe: ")
        self.opcions = ["Informe de seguiment", "Escolta'm"]
        self.alumne_etiqueta = QLabel(literal_alumnes)
        self.alumne_etiqueta.setMaximumWidth(50)
        self.tots_etiqueta = QLabel("Exportar informes de\ntots els alumnes? ")

        # Definim botons o elements clickables:
        self.seleccio_informe = QComboBox()
        self.seleccio_informe.addItems(self.opcions)
        self.seleccio_informe.setToolTip("Informe de seguiment de l'alumne")
        self.seleccio_informe.currentText()
        self.seleccio_informe.currentTextChanged.connect(self.seleccio_informe_canviat)
        self.alumne_seleccio = QComboBox()
        self.al_seleccionat = self.alumne_seleccio.currentText()
        self.alumne_seleccio.currentTextChanged.connect(self.canvi_alumne)
        self.alumnes_registrats = self.consultor_export.llista_alumnes_registres()
        self.alumne_seleccio.addItems(self.alumnes_registrats)
        self.desarBoto = QPushButton(icon=QIcon("src/icones/document-save-symbolic.svg"), text="Desar")
        self.desarBoto.setEnabled(False)
        self.boto_seleccio_carpeta = QPushButton(text="Selecciona carpeta")
        self.tots_check = QCheckBox()
        self.tots_check.setTristate(False)
        self.tots_check.clicked.connect(self.tots_seleccionat)
        self.boto_seleccio_carpeta.clicked.connect(self.seleccio_carpeta)
        self.boto_tornar = QPushButton(icon=QIcon("src/icones/draw-arrow-back.svg"), text="Torna")
        self.boto_tornar.clicked.connect(self.tornar)
        # Situem els elements:
        self.exportacio_disposicio.setHorizontalSpacing(2)
        self.exportacio_disposicio.addWidget(self.seleccio_tipus_informe, 0, 0)
        self.exportacio_disposicio.addWidget(self.seleccio_informe, 0, 1)
        self.exportacio_disposicio.addWidget(self.tots_etiqueta, 1, 0)
        self.exportacio_disposicio.addWidget(self.tots_check, 1, 1)
        self.exportacio_disposicio.addWidget(self.alumne_etiqueta, 2, 0)
        self.exportacio_disposicio.addWidget(self.alumne_seleccio, 2, 1)
        self.exportacio_disposicio.addWidget(self.boto_seleccio_carpeta, 3, 0)
        self.exportacio_disposicio.addWidget(self.desarBoto, 3, 1)
        self.exportacio_disposicio.addWidget(self.boto_tornar, 4, 0, 1, 2)

    def seleccio_informe_canviat(self):
        """
        S'executa quan canvia la selecció de l'informe.
        """
        if self.seleccio_informe.currentText() == "Escolta'm":
            self.seleccio_informe.setToolTip("Genera llistat dels escolta'm fets, per mesos")
            self.alumne_etiqueta.setEnabled(False)
            self.alumne_seleccio.setEnabled(False)
            self.tots_etiqueta.setEnabled(False)
            self.tots_check.setEnabled(False)
        elif self.seleccio_informe.currentText() == "Informe de seguiment":
            self.seleccio_informe.setToolTip("Informe de seguiment de l'alumne")
            self.alumne_etiqueta.setEnabled(True)
            self.alumne_seleccio.setEnabled(True)
            self.tots_etiqueta.setEnabled(True)
            self.tots_check.setEnabled(True)

    def tots_seleccionat(self):
        """
        Desactiva controls d'alumne si se selecciona l'opció d'exportar tots els alumnes.
        :return:
        """
        if self.tots_check.isChecked():
            self.alumne_seleccio.setEnabled(False)
        else:
            self.alumne_seleccio.setEnabled(True)

    def tornar(self):
        """
        Torna a la finestra anterior.
        """
        self.close()

    def canvi_alumne(self):
        """
        Modifica el nom de l'alumne seleccionat.
        :return:
        """
        self.al_seleccionat = self.alumne_seleccio.currentText()

    def seleccio_carpeta(self):
        """
        Selecciona la carpeta on desar els informes.
        """
        self.dialeg.setFileMode(QFileDialog.Directory)
        self.carpeta_seleccionada = self.dialeg.getExistingDirectory(self, "Selecciona carpeta")
        self.carpeta_seleccionada = self.carpeta_seleccionada + "/"
        if self.carpeta_seleccionada is not None:
            self.desarBoto.setEnabled(True)

    def desar(self):
        """
        Desa els informes seleccionats.
        """
        if self.seleccio_informe.currentText() == "Escolta'm":
            self.exportador_informes.export_escolta_m()
        elif self.seleccio_informe.currentText() == "Informe de seguiment":
            if self.tots_check.isChecked():
                for alumne in self.alumnes_registrats:
                    self.exportador_informes.export_informes_seguiment(alumne, self.carpeta_seleccionada)
            else:
                self.exportador_informes.export_informes_seguiment(self.al_seleccionat, self.carpeta_seleccionada)


class AssistentInicial(QWizard):
    def __init__(self):
        super().__init__()
        self.paginicdesc = QLabel("Aquesta aplicació serveix per a la gestió dels alumnes tutoritzats.\n"
                                  "S'ha detectat que no consten noms d'alumnes, registres previs ni dates de "
                                  "trimestre.\n "
                                  "A continuacio s'us demanara que introduiu aquestes dades.")
        self.pagina_inicial = QWizardPage()
        self.pagina_alumnes = QWizardPage()
        self.pagina_final = QWizardPage()
        self.setWindowTitle("Assistent d'inicialització")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(QSize(600, 400))
        self.configpagines()
        self.addPage(self.pagina_inicial)
        self.addPage(self.pagina_alumnes)
        self.addPage(self.pagina_final)
        self.button(QWizard.CancelButton).setText("Cancel·lar")
        self.acciocancela = QAction(app.quit())
        self.acciotanca = QAction(self.cancela())
        self.button(QWizard.CancelButton).addActions([self.acciocancela, self.acciotanca])

    def configpagines(self):
        # Afegim les pàgines:
        # Afegim pagina inicial:
        self.pagina_inicial.setTitle("Inicialització")
        self.pagina_inicial.setSubTitle("Inicialització de l'aplicació")
        paginainicialdistr = QVBoxLayout()
        self.paginicdesc.setWordWrap(True)
        paginainicialdistr.addWidget(self.paginicdesc)
        self.pagina_inicial.setLayout(paginainicialdistr)
        # Afegim i configurem pagina alumnes:
        dadesalumnesassist = DadesAlumnes()
        dadesalumnesassist.esborrarBoto.setEnabled(False)
        dadesalumnesassist.esborrarBoto.setVisible(False)
        dadesalumnesassist.tornarBoto.setEnabled(False)
        dadesalumnesassist.tornarBoto.setVisible(False)
        paginaaldist = QVBoxLayout()
        paginaaldist.addWidget(dadesalumnesassist)
        self.pagina_alumnes.setLayout(paginaaldist)
        # Afegim pagina final:
        datestrimestreassist = DatesTrimestre()
        datestrimestreassist.tornarBoto.setEnabled(False)
        datestrimestreassist.tornarBoto.setVisible(False)
        paginafinaldist = QVBoxLayout()
        self.pagina_final.setLayout(paginafinaldist)
        paginafinaldist.addWidget(datestrimestreassist)

    def cancela(self):
        self.close()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
