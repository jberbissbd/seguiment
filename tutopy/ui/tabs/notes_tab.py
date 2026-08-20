from PySide6.QtCore import QDate, QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QFormLayout, QHBoxLayout, QHeaderView,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from tutopy.ui.resources import set_button_icon

from tutopy.ui.widgets.debounced_line_edit import DebouncedLineEdit


class NotesTab(QWidget):
    """Taula i filtres de notes sense dependències de negoci."""

    filters_changed = Signal(dict)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        filters = QFormLayout()
        self.current_student_id = None
        self.category_filter = QComboBox()
        self.course_filter = QComboBox()
        self.content_filter = DebouncedLineEdit()
        self.content_filter.setPlaceholderText("Cercar en el contingut…")
        filters.addRow("Categoria:", self.category_filter)
        filters.addRow("Curs acadèmic:", self.course_filter)

        dates = QHBoxLayout()
        self.date_from_enabled = QCheckBox("Des de")
        self.date_from = self._date_edit()
        self.date_from.setEnabled(False)
        self.date_to_enabled = QCheckBox("Fins a")
        self.date_to = self._date_edit()
        self.date_to.setEnabled(False)
        dates.addWidget(self.date_from_enabled)
        dates.addWidget(self.date_from)
        dates.addWidget(self.date_to_enabled)
        dates.addWidget(self.date_to)
        dates.addStretch()
        filters.addRow("Dates:", dates)
        filters.addRow("Contingut:", self.content_filter)
        layout.addLayout(filters)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setObjectName("dangerButton")
        self.clear_button = QPushButton("Netejar filtres")
        set_button_icon(self.edit_button, "edit")
        set_button_icon(self.delete_button, "delete")
        set_button_icon(self.clear_button, "clear")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        actions.addWidget(self.clear_button)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Data", "Categoria", "Contingut"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        for column in range(2):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        self._connect_signals()

    def _date_edit(self) -> QDateEdit:
        edit = QDateEdit(QDate.currentDate())
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("dd/MM/yyyy")
        return edit

    def _connect_signals(self) -> None:
        self.category_filter.currentIndexChanged.connect(self._emit_filters)
        self.course_filter.currentIndexChanged.connect(self._emit_filters)
        self.content_filter.debounced_text_changed.connect(self._emit_filters)
        self.date_from_enabled.toggled.connect(self.date_from.setEnabled)
        self.date_from_enabled.toggled.connect(self._emit_filters)
        self.date_to_enabled.toggled.connect(self.date_to.setEnabled)
        self.date_to_enabled.toggled.connect(self._emit_filters)
        self.date_from.dateChanged.connect(self._emit_filters)
        self.date_to.dateChanged.connect(self._emit_filters)
        self.clear_button.clicked.connect(self.clear_filters)
        self.edit_button.clicked.connect(self._request_edit)
        self.delete_button.clicked.connect(self._request_delete)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.cellDoubleClicked.connect(
            lambda row, _column: self.edit_requested.emit(self._note_id_at(row))
        )

    def set_options(self, categories, courses) -> None:
        blockers = [
            QSignalBlocker(self.category_filter),
            QSignalBlocker(self.course_filter),
        ]
        self.category_filter.clear()
        self.category_filter.addItem("Totes les categories", None)
        for category in categories:
            self.category_filter.addItem(category.name, category.id)
        self.course_filter.clear()
        self.course_filter.addItem("Tots els cursos", None)
        for course in courses:
            self.course_filter.addItem(course.course, course.id)
        del blockers

    def set_student_context(self, student_id) -> None:
        self.current_student_id = student_id

    def filters(self) -> dict:
        result = {
            "student_id": self.current_student_id,
            "category_id": self.category_filter.currentData(),
            "course_id": self.course_filter.currentData(),
            "content": self.content_filter.text().strip() or None,
            "date_from": None,
            "date_to": None,
        }
        if self.date_from_enabled.isChecked():
            result["date_from"] = self.date_from.date().toString("yyyy-MM-dd")
        if self.date_to_enabled.isChecked():
            result["date_to"] = self.date_to.date().toString("yyyy-MM-dd")
        return result

    def clear_filters(self) -> None:
        self.category_filter.setCurrentIndex(0)
        self.course_filter.setCurrentIndex(0)
        self.date_from_enabled.setChecked(False)
        self.date_to_enabled.setChecked(False)
        self.content_filter.clear()
        self.content_filter.cancel_pending()
        self._emit_filters()

    def set_records(self, records) -> None:
        """Actualitza la taula in situ i conserva selecció i objectes de fila."""
        records = tuple(records)
        selected_id = self.current_note_id()
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(records))
            for row, record in enumerate(records):
                values = (
                    self._display_date(record.date),
                    record.category_name,
                    record.content,
                )
                for column, value in enumerate(values):
                    item = self.table.item(row, column)
                    if item is None:
                        item = QTableWidgetItem()
                        self.table.setItem(row, column, item)
                    item.setText(value)
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, record.note_id)
                if record.note_id == selected_id:
                    self.table.selectRow(row)
        finally:
            self.table.setUpdatesEnabled(True)
        self._selection_changed()

    def current_note_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self._note_id_at(rows[0].row()) if rows else None

    def _note_id_at(self, row: int):
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _selection_changed(self) -> None:
        selected = self.current_note_id() is not None
        self.edit_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def _request_edit(self) -> None:
        note_id = self.current_note_id()
        if note_id is not None:
            self.edit_requested.emit(note_id)

    def _request_delete(self) -> None:
        note_id = self.current_note_id()
        if note_id is not None:
            self.delete_requested.emit(note_id)

    def _emit_filters(self, *args) -> None:
        self.filters_changed.emit(self.filters())

    @staticmethod
    def _display_date(iso_date: str) -> str:
        date = QDate.fromString(iso_date, "yyyy-MM-dd")
        return date.toString("dd/MM/yyyy") if date.isValid() else iso_date
