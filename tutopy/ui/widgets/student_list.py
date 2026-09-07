"""Llista d'alumnes amb cerca, selecció i accions massives.

Mostra els alumnes en una `QListView` amb un model i un delegat, permet
cercar-los amb debounce i emet senyals per crear, editar, eliminar o
exportar-ne, sense consultar cap servei directament.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

from tutopy.ui.resources import set_button_icon
from tutopy.ui.widgets.debounced_line_edit import DebouncedLineEdit
from tutopy.ui.widgets.student_list_view import StudentListView


class StudentList(QFrame):
    """Llista visual d'alumnes; no consulta directament cap servei.

    Inclou un camp de cerca amb debounce de 180 ms (`DebouncedLineEdit`) que
    emet `search_changed` un cop l'usuari deixa d'escriure.
    """

    student_selected = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)
    search_changed = Signal(str)
    create_requested = Signal()
    batch_export_requested = Signal()
    bulk_edit_requested = Signal()
    note_create_requested = Signal(int)

    def __init__(self, parent=None):
        """Construeix la capçalera d'accions, el cercador i la llista d'alumnes."""
        super().__init__(parent)
        self.setObjectName("panel")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Alumnes")
        title.setObjectName("sectionTitle")
        self.create_button = QPushButton("Nou alumne")
        set_button_icon(self.create_button, "add")
        self.create_button.setObjectName("primaryButton")
        self.create_button.clicked.connect(self.create_requested)
        header.addWidget(title)
        header.addStretch()
        header_actions = QVBoxLayout()
        header_actions.setContentsMargins(0, 0, 0, 0)
        header_actions.setSpacing(6)
        self.batch_export_button = QPushButton("Exportar diversos…")
        set_button_icon(self.batch_export_button, "export")
        self.batch_export_button.setObjectName("secondaryButton")
        self.batch_export_button.setEnabled(False)
        self.batch_export_button.clicked.connect(self.batch_export_requested)
        self.bulk_edit_button = QPushButton("Edició massiva…")
        set_button_icon(self.bulk_edit_button, "edit")
        self.bulk_edit_button.setObjectName("secondaryButton")
        self.bulk_edit_button.setEnabled(False)
        self.bulk_edit_button.clicked.connect(self.bulk_edit_requested)
        header_actions.addWidget(self.create_button)
        header_actions.addWidget(self.bulk_edit_button)
        header_actions.addWidget(self.batch_export_button)
        header.addLayout(header_actions)
        layout.addLayout(header)

        self.search_input = DebouncedLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.debounced_text_changed.connect(self.search_changed)
        layout.addWidget(self.search_input)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar")
        set_button_icon(self.edit_button, "edit")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
        set_button_icon(self.delete_button, "delete")
        self.delete_button.setObjectName("dangerButton")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.edit_button.clicked.connect(self._request_edit)
        self.delete_button.clicked.connect(self._request_delete)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.list_widget = StudentListView()
        self.list_widget.setObjectName("studentListWidget")
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.selectionModel().currentChanged.connect(self._emit_selection)
        self.list_widget.note_requested.connect(self._request_note)
        self.list_widget.doubleClicked.connect(
            lambda item: self.edit_requested.emit(
                item.data(Qt.ItemDataRole.UserRole)
            )
        )
        layout.addWidget(self.list_widget, 1)

        self.empty_label = QLabel("Encara no hi ha alumnes.")
        self.empty_label.setObjectName("mutedText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

    def set_students(self, students) -> None:
        """Actualitza el model i conserva la selecció per identificador."""
        selected_id = self.current_student_id()
        model = self.list_widget.model()
        model.set_students(students)
        self.select_student(selected_id)
        has_students = model.rowCount() > 0
        self.list_widget.setVisible(has_students)
        self.empty_label.setVisible(not has_students)
        self.batch_export_button.setEnabled(has_students)
        self.bulk_edit_button.setEnabled(has_students)
        has_selection = self.current_student_id() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def current_student_id(self) -> int | None:
        """Retorna l'ID de l'alumne seleccionat, o None si no n'hi ha cap."""
        return self.list_widget.currentIndex().data(Qt.ItemDataRole.UserRole)

    def _emit_selection(self, current, previous=None) -> None:
        self.edit_button.setEnabled(current.isValid())
        self.delete_button.setEnabled(current.isValid())
        if current.isValid():
            self.student_selected.emit(current.data(Qt.ItemDataRole.UserRole))

    def select_student(self, student_id: int | None) -> None:
        """Selecciona l'alumne per identificador, si és present al model."""
        index = self.list_widget.model().student_index(student_id)
        if index.isValid():
            self.list_widget.setCurrentIndex(index)

    def _request_note(self, student_id: int) -> None:
        self.select_student(student_id)
        self.note_create_requested.emit(student_id)

    def _request_edit(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.edit_requested.emit(student_id)

    def _request_delete(self) -> None:
        student_id = self.current_student_id()
        if student_id is not None:
            self.delete_requested.emit(student_id)
