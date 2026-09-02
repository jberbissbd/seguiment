"""Diàleg de selecció múltiple d'alumnes per a una transferència."""

from collections.abc import Sequence

from PySide6.QtWidgets import QLabel, QWidget

from tutopy.models.messaging import Student
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog
from tutopy.ui.widgets.checkable_student_list import CheckableStudentListPanel


class TransferStudentSelectionDialog(BaseFormDialog):
    """Permet cercar i marcar un o diversos alumnes, mostrant-ne el grup."""

    def __init__(self, students: Sequence[Student], parent: QWidget | None = None):
        """Construeix el diàleg amb la llista d'alumnes marcables.

        Args:
            students: Alumnes que es poden marcar per transferir, amb cerca per nom,
                cognoms o grup mitjançant un camp de cerca amb `debounce`.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent, "Seleccionar alumnes per exportar")
        self.setMinimumSize(540, 480)
        self.layout.addWidget(QLabel("Selecciona els alumnes que vols transferir."))

        self.selection_panel = CheckableStudentListPanel(
            students,
            item_text=lambda s: f"{s.full_name} — Grup: {s.group_name or 'Sense grup'}",
            search_key=lambda s: f"{s.full_name} {s.group_name or 'Sense grup'}".casefold(),
        )
        self.search_input = self.selection_panel.search_input
        self.select_visible_button = self.selection_panel.select_visible_button
        self.clear_button = self.selection_panel.clear_button
        self.selection_label = self.selection_panel.selection_label
        self.student_list = self.selection_panel.student_list
        self.layout.addWidget(self.selection_panel)

        self._add_footer("Cal seleccionar almenys un alumne.", save_text="Continuar")

    def student_ids(self) -> list[int]:
        """Retorna els identificadors marcats en l'ordre visible."""
        return self.selection_panel.student_ids()

    def _select_visible(self) -> None:
        self.selection_panel.select_visible()

    def _is_valid(self) -> bool:
        return bool(self.student_ids())
