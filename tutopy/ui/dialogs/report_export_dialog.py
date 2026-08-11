from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QLabel,
    QListWidget, QListWidgetItem, QVBoxLayout,
)
from PySide6.QtCore import Qt


class ReportExportDialog(QDialog):
    def __init__(self, categories, parent=None, show_term_option=True):
        super().__init__(parent)
        self.setWindowTitle("Exportar informe")
        self.setMinimumSize(430, 430)
        layout = QVBoxLayout(self)
        description = QLabel(
            "Arrossega les categories per establir-ne l’ordre. Aquest ordre "
            "es recordarà per a les exportacions següents."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
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
        layout.addWidget(self.format_input)
        self.include_terms = QCheckBox("Incloure els trimestres configurats")
        self.include_terms.setChecked(True)
        self.include_terms.setVisible(show_term_option)
        layout.addWidget(self.include_terms)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Continuar")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.format_input.currentIndexChanged.connect(self._update_term_visibility)

    def category_order(self) -> list[int]:
        return [
            self.category_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.category_list.count())
        ]

    def export_format(self) -> str:
        return self.format_input.currentData()

    def _update_term_visibility(self) -> None:
        self.include_terms.setEnabled(self.export_format() == "xlsx")
