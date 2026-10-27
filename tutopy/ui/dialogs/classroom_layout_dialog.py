"""Diàleg per crear una nova distribució de taules d'aula."""

from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QSpinBox, QWidget

from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog
from tutopy.ui.widgets.classroom_layout_view import (
    TEACHER_MODE_LABELS, TEACHER_POSITION_LABELS,
)


class ClassroomLayoutDialog(BaseFormDialog):
    """Recull el nom, les mides i la taula del professor d'una distribució nova."""

    def __init__(self, group_name: str, parent: QWidget | None = None):
        """Construeix el diàleg per a una nova distribució del grup `group_name`."""
        super().__init__(parent, "Nova distribució")
        self.setMinimumWidth(380)
        self.group_name = group_name
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de la distribució")
        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 20)
        self.rows_input.setValue(4)
        self.columns_input = QSpinBox()
        self.columns_input.setRange(1, 20)
        self.columns_input.setValue(6)
        self.teacher_mode_input = QComboBox()
        for value, label in TEACHER_MODE_LABELS.items():
            self.teacher_mode_input.addItem(label, value)
        self.teacher_position_input = QComboBox()
        for value, label in TEACHER_POSITION_LABELS.items():
            self.teacher_position_input.addItem(label, value)
        form.addRow("Nom:", self.name_input)
        form.addRow("Files:", self.rows_input)
        form.addRow("Columnes:", self.columns_input)
        form.addRow("Taula del professor:", self.teacher_mode_input)
        form.addRow("Posició:", self.teacher_position_input)
        self.layout.addLayout(form)
        self._add_footer("El nom és obligatori.")

    def values(self) -> dict:
        """Retorna les dades introduïdes per crear la nova distribució."""
        return {
            "group_name": self.group_name,
            "name": self.name_input.text().strip(),
            "rows": self.rows_input.value(),
            "columns": self.columns_input.value(),
            "teacher_mode": self.teacher_mode_input.currentData(),
            "teacher_position": self.teacher_position_input.currentData(),
        }

    def _is_valid(self) -> bool:
        return bool(self.name_input.text().strip())
