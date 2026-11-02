"""Diàleg per crear una nova distribució de taules d'aula.

Ofereix exactament les mateixes opcions que "Aplicar plantilla"
(disposició, taula del professor, seients sobrants i ordre d'ompliment),
amb un camp de nom afegit al capdamunt: la distribució es crea ja amb la
forma i l'ompliment triats, en lloc de començar sempre com una quadrícula
buida que calgui omplir a mà o amb una plantilla a part.
"""

from PySide6.QtWidgets import QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget

from tutopy.models.classroom_layout import ClassroomLayout
from tutopy.ui.dialogs.classroom_layout_template_dialog import ClassroomLayoutTemplateDialog


class ClassroomLayoutDialog(ClassroomLayoutTemplateDialog):
    """Recull el nom i les opcions de plantilla d'una distribució nova."""

    def __init__(
        self, group_name: str, student_count: int, other_layouts: list[ClassroomLayout],
        defaults: dict, parent: QWidget | None = None,
    ):
        """Construeix el diàleg per a una nova distribució del grup `group_name`.

        Args:
            group_name: Grup al qual pertanyerà la distribució.
            student_count: Nombre d'alumnes del grup (seients necessaris).
            other_layouts: Altres distribucions del mateix grup, per a
                l'opció "Duplicar una existent".
            defaults: Valors inicials (de `PreferencesService`).
            parent: Widget pare de Qt, si escau.
        """
        self.group_name = group_name
        super().__init__(student_count, other_layouts, defaults, parent)
        self.setWindowTitle("Nova distribució")
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText("Crear")

    def _build_leading_fields(self, form_column: QVBoxLayout) -> None:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de la distribució")
        name_row = QFormLayout()
        name_row.addRow("Nom:", self.name_input)
        form_column.addLayout(name_row)

    def _accept_valid(self) -> None:
        if not self.name_input.text().strip():
            self._show_error("El nom és obligatori.")
        elif not super()._is_valid():
            self._show_error()
        else:
            self.accept()

    def values(self) -> dict:
        """Retorna el nom, el grup i totes les opcions de plantilla triades."""
        values = super().values()
        values["group_name"] = self.group_name
        values["name"] = self.name_input.text().strip()
        return values
