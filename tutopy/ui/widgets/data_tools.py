"""Panell d'eines de dades: importació massiva, transferència i trimestres.

Agrupa les accions de manteniment de dades que no pertanyen a la fitxa d'un
alumne concret: descàrrega de plantilla, importació de fulls de càlcul,
transferència entre instàncies, configuració del logotip dels informes,
dels trimestres i l'esborrat total de dades.
"""

from collections.abc import Iterable, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QHBoxLayout, QLabel, QLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QSizePolicy,
)

from tutopy.ui.resources import set_button_icon


class DataToolsView(QWidget):
    """Panell d'importació, transferència, informes i esborrat de dades.

    Cada botó del panell emet un senyal `*_requested`; aquesta vista no
    executa cap operació de negoci per si mateixa.
    """

    template_requested = Signal()
    import_requested = Signal()
    clear_requested = Signal()
    transfer_student_requested = Signal()
    transfer_all_requested = Signal()
    transfer_import_requested = Signal()
    category_order_requested = Signal()
    report_logo_requested = Signal()
    report_logo_remove_requested = Signal()
    term_create_requested = Signal()
    term_edit_requested = Signal(int)
    term_delete_requested = Signal(int)

    def __init__(self, parent=None):
        """Construeix els panells d'importació, transferència, informes i esborrat."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        import_panel = QFrame()
        import_panel.setObjectName("panel")
        import_layout = QVBoxLayout(import_panel)
        import_layout.addWidget(self._title("Importació massiva"))
        import_layout.addWidget(self._description(
            "Descarrega la plantilla, omple els fulls d’alumnes i categories i "
            "importa’ls en bloc des d’Excel o LibreOffice Calc."
        ))
        self.template_button = QPushButton("Descarregar plantilla XLSX")
        self.template_button.setObjectName("secondaryButton")
        self.import_button = QPushButton("Importar full de càlcul")
        set_button_icon(self.template_button, "template")
        set_button_icon(self.import_button, "import")
        self.import_button.setObjectName("primaryButton")
        import_layout.addWidget(self.template_button)
        import_layout.addWidget(self.import_button)

        transfer_panel = QFrame()
        transfer_panel.setObjectName("panel")
        transfer_layout = QVBoxLayout(transfer_panel)
        transfer_layout.addWidget(self._title("Transferència entre instàncies"))
        transfer_layout.addWidget(self._description(
            "Exporta alumnes amb notes, contactes, descriptors, historial i "
            "documents, o importa un paquet .tpy d’una altra instància."
        ))
        transfer_actions = QHBoxLayout()
        self.transfer_student_button = QPushButton("Exportar seleccionats")
        self.transfer_all_button = QPushButton("Exportar tots els alumnes")
        self.transfer_import_button = QPushButton("Importar paquet Tutopy")
        set_button_icon(self.transfer_student_button, "export")
        set_button_icon(self.transfer_all_button, "export")
        set_button_icon(self.transfer_import_button, "import")
        self.transfer_student_button.setObjectName("secondaryButton")
        self.transfer_all_button.setObjectName("secondaryButton")
        self.transfer_import_button.setObjectName("primaryButton")
        transfer_actions.addWidget(self.transfer_student_button)
        transfer_actions.addWidget(self.transfer_all_button)
        transfer_actions.addWidget(self.transfer_import_button)
        transfer_layout.addLayout(transfer_actions)

        report_panel = QFrame()
        report_panel.setObjectName("panel")
        self.report_panel = report_panel
        report_layout = QVBoxLayout(report_panel)
        report_layout.addWidget(self._title("Informes i trimestres"))
        report_layout.addWidget(self._description(
            "Configura la presentació i l’organització temporal dels informes."
        ))

        category_panel = QFrame()
        category_panel.setObjectName("settingsGroup")
        category_layout = QVBoxLayout(category_panel)
        category_layout.addWidget(self._subtitle("Ordre de les categories"))
        category_layout.addWidget(self._description(
            "Estableix l’ordre en què apareixen les categories als informes."
        ))
        self.category_order_button = QPushButton("Ordenar categories")
        set_button_icon(self.category_order_button, "order")
        self.category_order_button.setObjectName("secondaryButton")
        category_layout.addWidget(self.category_order_button)
        report_layout.addWidget(category_panel)

        logo_panel = QFrame()
        logo_panel.setObjectName("settingsGroup")
        logo_layout = QVBoxLayout(logo_panel)
        logo_layout.addWidget(self._subtitle("Logotip dels informes"))
        logo_layout.addWidget(self._description(
            "Selecciona la imatge que apareixerà al bloc inicial dels informes de text i PDF."
        ))
        logo_actions = QHBoxLayout()
        self.report_logo_label = QLabel("Logotip: cap")
        self.report_logo_label.setObjectName("mutedText")
        self.report_logo_button = QPushButton("Seleccionar logotip")
        self.report_logo_button.setObjectName("secondaryButton")
        self.report_logo_remove_button = QPushButton("Eliminar logotip")
        set_button_icon(self.report_logo_button, "image")
        set_button_icon(self.report_logo_remove_button, "delete")
        self.report_logo_remove_button.setObjectName("secondaryButton")
        self.report_logo_remove_button.setEnabled(False)
        logo_actions.addWidget(self.report_logo_label, 1)
        logo_actions.addWidget(self.report_logo_button)
        logo_actions.addWidget(self.report_logo_remove_button)
        logo_layout.addLayout(logo_actions)
        report_layout.addWidget(logo_panel)

        term_panel = QFrame()
        term_panel.setObjectName("settingsGroup")
        term_layout = QVBoxLayout(term_panel)
        term_layout.addWidget(self._subtitle("Configuració de trimestres"))
        term_layout.addWidget(self._description(
            "Defineix per a cada curs i grup les dates d’inici del segon i tercer trimestre."
        ))
        term_actions = QHBoxLayout()
        self.term_create_button = QPushButton("Nova configuració")
        self.term_create_button.setObjectName("primaryButton")
        self.term_edit_button = QPushButton("Editar")
        self.term_edit_button.setObjectName("secondaryButton")
        self.term_delete_button = QPushButton("Eliminar")
        set_button_icon(self.term_create_button, "add")
        set_button_icon(self.term_edit_button, "edit")
        set_button_icon(self.term_delete_button, "delete")
        self.term_delete_button.setObjectName("dangerButton")
        self.term_edit_button.setEnabled(False)
        self.term_delete_button.setEnabled(False)
        term_actions.addWidget(self.term_create_button)
        term_actions.addWidget(self.term_edit_button)
        term_actions.addWidget(self.term_delete_button)
        term_actions.addStretch()
        term_layout.addLayout(term_actions)
        self.term_table = QTableWidget(0, 4)
        self.term_table.setHorizontalHeaderLabels(
            ["Curs", "Grup", "Inici 2n\ntrimestre", "Inici 3r\ntrimestre"]
        )
        self.term_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.term_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.term_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.term_table.verticalHeader().hide()
        term_header = self.term_table.horizontalHeader()
        term_header.setStretchLastSection(False)
        term_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        term_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        term_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        term_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        two_line_height = term_header.fontMetrics().lineSpacing() * 2 + 12
        term_header.setMinimumHeight(two_line_height)
        term_header.setFixedHeight(two_line_height)
        self.term_table.setMaximumHeight(190)
        term_layout.addWidget(self.term_table)
        report_layout.addWidget(term_panel)

        danger_panel = QFrame()
        danger_panel.setObjectName("panel")
        danger_layout = QVBoxLayout(danger_panel)
        danger_layout.addWidget(self._title("Zona perillosa"))
        danger_layout.addWidget(self._description(
            "Elimina definitivament alumnes, notes, categories, contactes, descriptors, documents i cursos."
        ))
        self.clear_button = QPushButton("Eliminar totes les dades")
        set_button_icon(self.clear_button, "delete")
        self.clear_button.setObjectName("dangerButton")
        danger_layout.addWidget(self.clear_button)

        action_buttons = (
            self.template_button, self.import_button, self.category_order_button,
            self.report_logo_button, self.report_logo_remove_button,
            self.term_create_button, self.term_edit_button, self.term_delete_button,
            self.clear_button,
            self.transfer_student_button, self.transfer_all_button,
            self.transfer_import_button,
        )
        for button in action_buttons:
            button.setMinimumHeight(38)
            button.setSizePolicy(
                button.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Fixed
            )

        layout.addWidget(import_panel)
        layout.addWidget(transfer_panel)
        layout.addWidget(danger_panel)
        layout.addStretch()
        self.template_button.clicked.connect(self.template_requested)
        self.import_button.clicked.connect(self.import_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.transfer_student_button.clicked.connect(self.transfer_student_requested)
        self.transfer_all_button.clicked.connect(self.transfer_all_requested)
        self.transfer_import_button.clicked.connect(self.transfer_import_requested)
        self.category_order_button.clicked.connect(self.category_order_requested)
        self.report_logo_button.clicked.connect(self.report_logo_requested)
        self.report_logo_remove_button.clicked.connect(self.report_logo_remove_requested)
        self.term_create_button.clicked.connect(self.term_create_requested)
        self.term_edit_button.clicked.connect(self._request_term_edit)
        self.term_delete_button.clicked.connect(self._request_term_delete)
        self.term_table.itemSelectionChanged.connect(self._term_selection_changed)

    def set_term_configurations(self, rows: Iterable[tuple[int, Sequence]]) -> None:
        """Omple la taula de trimestres.

        Args:
            rows: Iterable de tuples `(id_configuració, valors_de_columna)`.
        """
        self.term_table.setRowCount(0)
        for configuration_id, values in rows:
            row = self.term_table.rowCount()
            self.term_table.insertRow(row)
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, configuration_id)
                self.term_table.setItem(row, column, item)
        self._term_selection_changed()

    def set_report_logo(self, filename: str | None) -> None:
        """Actualitza l'etiqueta del logotip i habilita el botó d'eliminar-lo.

        Args:
            filename: Nom del fitxer seleccionat, o `None` si no n'hi ha.
        """
        self.report_logo_label.setText(f"Logotip: {filename}" if filename else "Logotip: cap")
        self.report_logo_remove_button.setEnabled(bool(filename))

    def current_term_configuration_id(self):
        """Retorna l'ID de la configuració de trimestres seleccionada, o `None`."""
        rows = self.term_table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.term_table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def _term_selection_changed(self):
        enabled = self.current_term_configuration_id() is not None
        self.term_edit_button.setEnabled(enabled)
        self.term_delete_button.setEnabled(enabled)

    def _request_term_edit(self):
        configuration_id = self.current_term_configuration_id()
        if configuration_id is not None:
            self.term_edit_requested.emit(configuration_id)

    def _request_term_delete(self):
        configuration_id = self.current_term_configuration_id()
        if configuration_id is not None:
            self.term_delete_requested.emit(configuration_id)

    @staticmethod
    def _title(text):
        label = QLabel(text)
        label.setObjectName("studentName")
        return label

    @staticmethod
    def _description(text):
        label = QLabel(text)
        label.setObjectName("mutedText")
        label.setWordWrap(True)
        return label

    @staticmethod
    def _subtitle(text):
        label = QLabel(text)
        label.setObjectName("settingsTitle")
        return label
