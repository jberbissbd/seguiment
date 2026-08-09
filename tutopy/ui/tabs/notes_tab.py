from PySide6.QtCore import QDate, QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QFormLayout, QHBoxLayout, QHeaderView,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


class NotesTab(QWidget):
    """Taula i filtres de notes sense dependències de negoci."""

    filters_changed = Signal(dict)
    create_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        filters = QFormLayout()
        self.student_filter = QComboBox()
        self.category_filter = QComboBox()
        self.course_filter = QComboBox()
        self.content_filter = QLineEdit()
        self.content_filter.setPlaceholderText("Cercar en el contingut…")
        filters.addRow("Alumne:", self.student_filter)
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
        self.create_button = QPushButton("Nova nota")
        self.create_button.setObjectName("primaryButton")
        self.edit_button = QPushButton("Editar")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setObjectName("dangerButton")
        self.clear_button = QPushButton("Netejar filtres")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        actions.addWidget(self.create_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        actions.addWidget(self.clear_button)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Data", "Alumne", "Grup", "Categoria", "Contingut"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        for column in range(4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        self._connect_signals()

    def _date_edit(self) -> QDateEdit:
        edit = QDateEdit(QDate.currentDate())
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("dd/MM/yyyy")
        return edit

    def _connect_signals(self) -> None:
        self.student_filter.currentIndexChanged.connect(self._emit_filters)
        self.category_filter.currentIndexChanged.connect(self._emit_filters)
        self.course_filter.currentIndexChanged.connect(self._emit_filters)
        self.content_filter.textChanged.connect(self._emit_filters)
        self.date_from_enabled.toggled.connect(self.date_from.setEnabled)
        self.date_from_enabled.toggled.connect(self._emit_filters)
        self.date_to_enabled.toggled.connect(self.date_to.setEnabled)
        self.date_to_enabled.toggled.connect(self._emit_filters)
        self.date_from.dateChanged.connect(self._emit_filters)
        self.date_to.dateChanged.connect(self._emit_filters)
        self.clear_button.clicked.connect(self.clear_filters)
        self.create_button.clicked.connect(self.create_requested)
        self.edit_button.clicked.connect(self._request_edit)
        self.delete_button.clicked.connect(self._request_delete)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.cellDoubleClicked.connect(
            lambda row, _column: self.edit_requested.emit(self._note_id_at(row))
        )

    def set_options(self, students, categories, courses) -> None:
        blockers = [
            QSignalBlocker(self.student_filter),
            QSignalBlocker(self.category_filter),
            QSignalBlocker(self.course_filter),
        ]
        self.student_filter.clear()
        self.student_filter.addItem("Tots els alumnes", None)
        for student in students:
            label = (
                f"{student.full_name} · {student.group_name or 'Sense grup'} "
                f"· {student.uuid[:8]}"
            )
            self.student_filter.addItem(label, student.id)
        self.category_filter.clear()
        self.category_filter.addItem("Totes les categories", None)
        for category in categories:
            self.category_filter.addItem(category.name, category.id)
        self.course_filter.clear()
        self.course_filter.addItem("Tots els cursos", None)
        for course in courses:
            self.course_filter.addItem(course.course, course.id)
        del blockers

    def set_student_filter(self, student_id) -> None:
        index = self.student_filter.findData(student_id)
        self.student_filter.setCurrentIndex(max(index, 0))

    def filters(self) -> dict:
        result = {
            "student_id": self.student_filter.currentData(),
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
        self.student_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.course_filter.setCurrentIndex(0)
        self.date_from_enabled.setChecked(False)
        self.date_to_enabled.setChecked(False)
        self.content_filter.clear()
        self._emit_filters()

    def set_records(self, records) -> None:
        selected_id = self.current_note_id()
        self.table.setRowCount(0)
        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (
                self._display_date(record.date), record.student_name,
                record.group_name, record.category_name, record.content,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, record.note_id)
                self.table.setItem(row, column, item)
            if record.note_id == selected_id:
                self.table.selectRow(row)
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
