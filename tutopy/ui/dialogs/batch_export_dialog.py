"""Diàleg per exportar informes de diversos alumnes alhora."""

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QLabel, QListWidget,
    QListWidgetItem, QWidget,
)

from tutopy.models.messaging import Category, Student
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog
from tutopy.ui.widgets.checkable_student_list import CheckableStudentListPanel


class BatchExportDialog(BaseFormDialog):
    """Selecciona diversos alumnes i les opcions comunes d'exportació."""

    def __init__(
        self, students: Sequence[Student], categories: Sequence[Category],
        parent: QWidget | None = None,
    ):
        """Construeix el diàleg amb els alumnes i categories disponibles.

        Args:
            students: Alumnes que es poden marcar per exportar, amb cerca per nom,
                cognoms o grup mitjançant un camp de cerca amb `debounce`.
            categories: Categories disponibles, per definir-ne l'ordre a l'informe.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent, "Exportar diversos alumnes")
        self.setMinimumSize(560, 620)

        self.layout.addWidget(QLabel("Selecciona els alumnes que vols exportar."))
        self.selection_panel = CheckableStudentListPanel(
            students,
            item_text=lambda s: f"{s.filing_name} — {s.group_name or 'Sense grup'}",
            search_key=lambda s: f"{s.name} {s.surnames} {s.group_name}".casefold(),
        )
        self.search_input = self.selection_panel.search_input
        self.select_visible_button = self.selection_panel.select_visible_button
        self.clear_button = self.selection_panel.clear_button
        self.selection_label = self.selection_panel.selection_label
        self.student_list = self.selection_panel.student_list
        self.layout.addWidget(self.selection_panel, 2)

        self.layout.addWidget(QLabel("Ordre de les categories"))
        self.category_list = QListWidget()
        self.category_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            self.category_list.addItem(item)
        self.layout.addWidget(self.category_list, 1)

        self.layout.addWidget(QLabel("Format de l’informe"))
        self.format_input = QComboBox()
        self.format_input.addItem("Full de càlcul Excel (.xlsx)", "xlsx")
        self.format_input.addItem("Document de text (.docx)", "docx")
        self.format_input.addItem("Document OpenDocument (.odt)", "odt")
        self.format_input.addItem("Document PDF (.pdf)", "pdf")
        self.layout.addWidget(self.format_input)
        self.include_terms = QCheckBox("Incloure els trimestres configurats")
        self.include_terms.setChecked(True)
        self.include_documents = QCheckBox(
            "Incloure els documents, classificats per curs"
        )
        self.layout.addWidget(self.include_terms)
        self.layout.addWidget(self.include_documents)

        self._add_footer("Cal seleccionar almenys un alumne.", save_text="Continuar")
        self.format_input.currentIndexChanged.connect(self._update_options)

    def student_ids(self) -> list[int]:
        """Retorna els identificadors dels alumnes marcats."""
        return self.selection_panel.student_ids()

    def category_order(self) -> list[int]:
        """Retorna els identificadors de categoria en l'ordre triat per l'usuari."""
        return [
            self.category_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.category_list.count())
        ]

    def export_format(self) -> str:
        """Retorna el format d'exportació seleccionat (`xlsx`, `docx`, `odt` o `pdf`)."""
        return self.format_input.currentData()

    def _select_visible(self) -> None:
        self.selection_panel.select_visible()

    def _update_options(self) -> None:
        self.include_terms.setEnabled(self.export_format() == "xlsx")

    def _is_valid(self) -> bool:
        return bool(self.student_ids())
