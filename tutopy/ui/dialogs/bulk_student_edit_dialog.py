"""Diàleg per editar diversos alumnes alhora en una taula."""

from collections.abc import Sequence

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from tutopy.models.messaging import Student
from tutopy.ui.resources import set_dialog_button_icons


class BulkStudentEditDialog(QDialog):
    """Edita diversos alumnes i aplica opcionalment un grup a files seleccionades."""

    def __init__(
        self, students: Sequence[Student], groups: Sequence[str] = (),
        parent: QWidget | None = None,
    ):
        """Construeix la taula d'edició amb una fila per alumne.

        Args:
            students: Alumnes a mostrar i editar, un per fila.
            groups: Noms de grup existents per emplenar el desplegable d'assignació ràpida.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent)
        self.setWindowTitle("Edició massiva d’alumnes")
        self.setMinimumSize(760, 560)
        self._original = {
            student.id: (student.name, student.surnames, student.group_name)
            for student in students
        }
        layout = QVBoxLayout(self)
        description = QLabel(
            "Edita directament les cel·les. Els canvis de grup utilitzaran "
            "la mateixa data efectiva."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        group_actions = QHBoxLayout()
        group_actions.addWidget(QLabel("Grup per a les files seleccionades:"))
        self.group_input = QComboBox()
        self.group_input.setEditable(True)
        self.group_input.addItems(groups)
        self.apply_group_button = QPushButton("Aplicar grup")
        group_actions.addWidget(self.group_input, 1)
        group_actions.addWidget(self.apply_group_button)
        layout.addLayout(group_actions)

        self.table = QTableWidget(len(students), 3)
        self.table.setHorizontalHeaderLabels(("Nom", "Cognoms", "Grup"))
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        for row, student in enumerate(students):
            name = QTableWidgetItem(student.name)
            name.setData(Qt.ItemDataRole.UserRole, student.id)
            self.table.setItem(row, 0, name)
            self.table.setItem(row, 1, QTableWidgetItem(student.surnames))
            self.table.setItem(row, 2, QTableWidgetItem(student.group_name))
        layout.addWidget(self.table, 1)

        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Data efectiva dels canvis de grup:"))
        self.change_date = QDateEdit(QDate.currentDate())
        self.change_date.setCalendarPopup(True)
        self.change_date.setDisplayFormat("dd/MM/yyyy")
        date_row.addWidget(self.change_date)
        date_row.addStretch()
        layout.addLayout(date_row)

        self.validation_label = QLabel()
        self.validation_label.setObjectName("errorText")
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(
            "Aplicar canvis"
        )
        set_dialog_button_icons(self.buttons)
        layout.addWidget(self.buttons)

        self.apply_group_button.clicked.connect(self._apply_group)
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)

    def changes(self) -> list[dict]:
        """Retorna només les files que difereixen del snapshot inicial."""
        changes = []
        for row in range(self.table.rowCount()):
            student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            values = tuple(
                self.table.item(row, column).text().strip() for column in range(3)
            )
            if values != self._original[student_id]:
                changes.append({
                    "student_id": student_id,
                    "name": values[0],
                    "surnames": values[1],
                    "group_name": values[2],
                })
        return changes

    def effective_date(self) -> str:
        """Retorna la data efectiva dels canvis de grup en format ISO."""
        return self.change_date.date().toString(Qt.DateFormat.ISODate)

    def _apply_group(self) -> None:
        group = self.group_input.currentText().strip()
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        if not group or not rows:
            self._show_error("Selecciona files i indica un grup.")
            return
        for row in rows:
            self.table.item(row, 2).setText(group)
        self.validation_label.hide()

    def _validate_and_accept(self) -> None:
        changes = self.changes()
        if not changes:
            self._show_error("No s’ha modificat cap alumne.")
            return
        if any(not item["name"] or not item["surnames"] for item in changes):
            self._show_error("El nom i els cognoms són obligatoris.")
            return
        if any(not item["group_name"] for item in changes):
            self._show_error("El grup no pot estar buit en una fila modificada.")
            return
        self.accept()

    def _show_error(self, message: str) -> None:
        self.validation_label.setText(message)
        self.validation_label.show()
