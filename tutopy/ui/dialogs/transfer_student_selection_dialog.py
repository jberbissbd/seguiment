"""Diàleg de selecció múltiple d'alumnes per a una transferència."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout,
)


class TransferStudentSelectionDialog(QDialog):
    """Permet cercar i marcar un o diversos alumnes, mostrant-ne el grup."""

    def __init__(self, students, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar alumnes per exportar")
        self.setMinimumSize(540, 480)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Selecciona els alumnes que vols transferir."))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)

        actions = QHBoxLayout()
        self.select_visible_button = QPushButton("Seleccionar visibles")
        self.clear_button = QPushButton("Desmarcar tots")
        self.selection_label = QLabel("0 alumnes seleccionats")
        actions.addWidget(self.select_visible_button)
        actions.addWidget(self.clear_button)
        actions.addStretch()
        actions.addWidget(self.selection_label)
        layout.addLayout(actions)

        self.student_list = QListWidget()
        for student in students:
            group = student.group_name or "Sense grup"
            item = QListWidgetItem(f"{student.full_name} — Grup: {group}")
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            item.setData(
                Qt.ItemDataRole.UserRole + 1,
                f"{student.full_name} {group}".casefold(),
            )
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.student_list.addItem(item)
        layout.addWidget(self.student_list)

        self.validation_label = QLabel("Cal seleccionar almenys un alumne.")
        self.validation_label.setObjectName("errorText")
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(
            "Continuar"
        )
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.search_input.textChanged.connect(self._filter_students)
        self.select_visible_button.clicked.connect(self._select_visible)
        self.clear_button.clicked.connect(self._clear_selection)
        self.student_list.itemChanged.connect(self._update_selection_label)

    def student_ids(self) -> list[int]:
        """Retorna els identificadors marcats en l'ordre visible."""
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for row in range(self.student_list.count())
            if (item := self.student_list.item(row)).checkState()
            == Qt.CheckState.Checked
        ]

    def _filter_students(self, query: str) -> None:
        query = query.strip().casefold()
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            item.setHidden(query not in item.data(Qt.ItemDataRole.UserRole + 1))

    def _select_visible(self) -> None:
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)

    def _clear_selection(self) -> None:
        for row in range(self.student_list.count()):
            self.student_list.item(row).setCheckState(Qt.CheckState.Unchecked)

    def _update_selection_label(self, _item=None) -> None:
        self.selection_label.setText(
            f"{len(self.student_ids())} alumnes seleccionats"
        )

    def _accept_valid(self) -> None:
        if not self.student_ids():
            self.validation_label.show()
            return
        self.accept()
