from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)


class DataToolsView(QWidget):
    template_requested = Signal()
    import_requested = Signal()
    clear_requested = Signal()
    category_order_requested = Signal()
    report_logo_requested = Signal()
    report_logo_remove_requested = Signal()
    term_create_requested = Signal()
    term_edit_requested = Signal(int)
    term_delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        import_panel = QFrame()
        import_panel.setObjectName("panel")
        import_layout = QVBoxLayout(import_panel)
        import_layout.addWidget(self._title("Importació massiva"))
        import_layout.addWidget(self._description(
            "Descarrega la plantilla, omple els fulls d’alumnes i categories i importa’ls en bloc."
        ))
        self.template_button = QPushButton("Descarregar plantilla XLSX")
        self.template_button.setObjectName("secondaryButton")
        self.import_button = QPushButton("Importar full de càlcul")
        self.import_button.setObjectName("primaryButton")
        import_layout.addWidget(self.template_button)
        import_layout.addWidget(self.import_button)

        report_panel = QFrame()
        report_panel.setObjectName("panel")
        report_layout = QVBoxLayout(report_panel)
        report_layout.addWidget(self._title("Informes i trimestres"))
        report_layout.addWidget(self._description(
            "Defineix l’ordre de les categories i les dates d’inici del segon i tercer trimestre."
        ))
        self.category_order_button = QPushButton("Ordenar categories")
        self.category_order_button.setObjectName("secondaryButton")
        report_layout.addWidget(self.category_order_button)
        logo_actions = QHBoxLayout()
        self.report_logo_label = QLabel("Logotip: cap")
        self.report_logo_label.setObjectName("mutedText")
        self.report_logo_button = QPushButton("Seleccionar logotip")
        self.report_logo_button.setObjectName("secondaryButton")
        self.report_logo_remove_button = QPushButton("Eliminar logotip")
        self.report_logo_remove_button.setObjectName("secondaryButton")
        self.report_logo_remove_button.setEnabled(False)
        logo_actions.addWidget(self.report_logo_label, 1)
        logo_actions.addWidget(self.report_logo_button)
        logo_actions.addWidget(self.report_logo_remove_button)
        report_layout.addLayout(logo_actions)
        term_actions = QHBoxLayout()
        self.term_create_button = QPushButton("Nova configuració")
        self.term_create_button.setObjectName("primaryButton")
        self.term_edit_button = QPushButton("Editar")
        self.term_edit_button.setObjectName("secondaryButton")
        self.term_delete_button = QPushButton("Eliminar")
        self.term_delete_button.setObjectName("dangerButton")
        self.term_edit_button.setEnabled(False)
        self.term_delete_button.setEnabled(False)
        term_actions.addWidget(self.term_create_button)
        term_actions.addWidget(self.term_edit_button)
        term_actions.addWidget(self.term_delete_button)
        term_actions.addStretch()
        report_layout.addLayout(term_actions)
        self.term_table = QTableWidget(0, 4)
        self.term_table.setHorizontalHeaderLabels(
            ["Curs", "Grup", "Inici 2n trimestre", "Inici 3r trimestre"]
        )
        self.term_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.term_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.term_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.term_table.verticalHeader().hide()
        self.term_table.horizontalHeader().setStretchLastSection(True)
        self.term_table.setMaximumHeight(190)
        report_layout.addWidget(self.term_table)

        danger_panel = QFrame()
        danger_panel.setObjectName("panel")
        danger_layout = QVBoxLayout(danger_panel)
        danger_layout.addWidget(self._title("Zona perillosa"))
        danger_layout.addWidget(self._description(
            "Elimina definitivament alumnes, notes, categories, contactes, descriptors, documents i cursos."
        ))
        self.clear_button = QPushButton("Eliminar totes les dades")
        self.clear_button.setObjectName("dangerButton")
        danger_layout.addWidget(self.clear_button)

        layout.addWidget(import_panel)
        layout.addWidget(report_panel)
        layout.addWidget(danger_panel)
        layout.addStretch()
        self.template_button.clicked.connect(self.template_requested)
        self.import_button.clicked.connect(self.import_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.category_order_button.clicked.connect(self.category_order_requested)
        self.report_logo_button.clicked.connect(self.report_logo_requested)
        self.report_logo_remove_button.clicked.connect(self.report_logo_remove_requested)
        self.term_create_button.clicked.connect(self.term_create_requested)
        self.term_edit_button.clicked.connect(self._request_term_edit)
        self.term_delete_button.clicked.connect(self._request_term_delete)
        self.term_table.itemSelectionChanged.connect(self._term_selection_changed)

    def set_term_configurations(self, rows) -> None:
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
        self.report_logo_label.setText(f"Logotip: {filename}" if filename else "Logotip: cap")
        self.report_logo_remove_button.setEnabled(bool(filename))

    def current_term_configuration_id(self):
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
