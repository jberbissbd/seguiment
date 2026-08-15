from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout,
)

from tutopy.ui.resources import set_button_icon, set_dialog_button_icons


class BatchExportDialog(QDialog):
    """Selecciona diversos alumnes i les opcions comunes d'exportació."""

    def __init__(self, students, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar diversos alumnes")
        self.setMinimumSize(560, 620)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Selecciona els alumnes que vols exportar."))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)
        selection_actions = QHBoxLayout()
        self.select_visible_button = QPushButton("Seleccionar visibles")
        self.clear_button = QPushButton("Desmarcar tots")
        set_button_icon(self.select_visible_button, "select")
        set_button_icon(self.clear_button, "deselect")
        self.selection_label = QLabel("0 alumnes seleccionats")
        selection_actions.addWidget(self.select_visible_button)
        selection_actions.addWidget(self.clear_button)
        selection_actions.addStretch()
        selection_actions.addWidget(self.selection_label)
        layout.addLayout(selection_actions)

        self.student_list = QListWidget()
        for student in students:
            item = QListWidgetItem(
                f"{student.filing_name} — {student.group_name or 'Sense grup'}"
            )
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            item.setData(
                Qt.ItemDataRole.UserRole + 1,
                f"{student.name} {student.surnames} {student.group_name}".casefold(),
            )
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.student_list.addItem(item)
        layout.addWidget(self.student_list, 2)

        layout.addWidget(QLabel("Ordre de les categories"))
        self.category_list = QListWidget()
        self.category_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            self.category_list.addItem(item)
        layout.addWidget(self.category_list, 1)

        layout.addWidget(QLabel("Format de l’informe"))
        self.format_input = QComboBox()
        self.format_input.addItem("Full de càlcul Excel (.xlsx)", "xlsx")
        self.format_input.addItem("Document de text (.docx)", "docx")
        self.format_input.addItem("Document OpenDocument (.odt)", "odt")
        self.format_input.addItem("Document PDF (.pdf)", "pdf")
        layout.addWidget(self.format_input)
        self.include_terms = QCheckBox("Incloure els trimestres configurats")
        self.include_terms.setChecked(True)
        self.include_documents = QCheckBox(
            "Incloure els documents, classificats per curs"
        )
        layout.addWidget(self.include_terms)
        layout.addWidget(self.include_documents)

        self.validation_label = QLabel("Cal seleccionar almenys un alumne.")
        self.validation_label.setObjectName("errorText")
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText("Continuar")
        set_dialog_button_icons(self.buttons)
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.search_input.textChanged.connect(self._filter_students)
        self.select_visible_button.clicked.connect(self._select_visible)
        self.clear_button.clicked.connect(self._clear_selection)
        self.student_list.itemChanged.connect(self._update_selection_label)
        self.format_input.currentIndexChanged.connect(self._update_options)

    def student_ids(self) -> list[int]:
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for row in range(self.student_list.count())
            if (item := self.student_list.item(row)).checkState() == Qt.CheckState.Checked
        ]

    def category_order(self) -> list[int]:
        return [
            self.category_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.category_list.count())
        ]

    def export_format(self) -> str:
        return self.format_input.currentData()

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
        count = len(self.student_ids())
        self.selection_label.setText(f"{count} alumnes seleccionats")

    def _update_options(self) -> None:
        self.include_terms.setEnabled(self.export_format() == "xlsx")

    def _accept_valid(self) -> None:
        if not self.student_ids():
            self.validation_label.show()
            return
        self.accept()
