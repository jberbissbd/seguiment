"""Diàleg per configurar l'exportació de l'informe d'un sol alumne."""

from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QLabel,
    QListWidget, QListWidgetItem, QVBoxLayout,
)

from tutopy.ui.resources import set_dialog_button_icons
from PySide6.QtCore import Qt


class ReportExportDialog(QDialog):
    """Selecciona l'ordre de les categories i el format de sortida de l'informe."""

    def __init__(self, categories, parent=None, show_term_option=True):
        """Construeix el diàleg amb les categories disponibles per ordenar.

        Args:
            categories: Categories disponibles, per definir-ne l'ordre a l'informe.
            parent: Widget pare de Qt, si escau.
            show_term_option: Si cal mostrar les opcions de trimestres i documents,
                que no s'apliquen als formats de document de text.
        """
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
        self.format_input.addItem("Document OpenDocument (.odt)", "odt")
        self.format_input.addItem("Document PDF (.pdf)", "pdf")
        layout.addWidget(self.format_input)
        self.include_terms = QCheckBox("Incloure els trimestres configurats")
        self.include_terms.setChecked(True)
        self.include_terms.setVisible(show_term_option)
        layout.addWidget(self.include_terms)
        self.include_documents = QCheckBox("Incloure els documents, classificats per curs")
        self.include_documents.setVisible(show_term_option)
        layout.addWidget(self.include_documents)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Continuar")
        set_dialog_button_icons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.format_input.currentIndexChanged.connect(self._update_term_visibility)
        self._update_term_visibility()

    def category_order(self) -> list[int]:
        """Retorna els identificadors de categoria en l'ordre triat per l'usuari."""
        return [
            self.category_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.category_list.count())
        ]

    def export_format(self) -> str:
        """Retorna el format d'exportació seleccionat (`xlsx`, `docx`, `odt` o `pdf`)."""
        return self.format_input.currentData()

    def _update_term_visibility(self) -> None:
        is_text_document = self.export_format() in {"docx", "odt", "pdf"}
        self.include_terms.setEnabled(not is_text_document)
