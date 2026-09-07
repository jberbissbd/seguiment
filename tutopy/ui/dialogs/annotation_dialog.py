"""Diàleg per crear o editar un descriptor general d'un alumne."""

from PySide6.QtWidgets import QPlainTextEdit, QWidget

from tutopy.models.messaging import StudentAnnotation
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog


class AnnotationDialog(BaseFormDialog):
    """Recull el text d'un descriptor general, nou o existent."""

    def __init__(
        self, parent: QWidget | None = None,
        annotation: StudentAnnotation | None = None,
    ):
        """Construeix el diàleg, precarregant el contingut si s'edita un descriptor existent.

        Args:
            parent: Widget pare de Qt, si escau.
            annotation: Descriptor existent a editar, o `None` per crear-ne un de nou.
        """
        super().__init__(parent, "Editar descriptor" if annotation else "Nou descriptor")
        self.content_input = QPlainTextEdit(annotation.content if annotation else "")
        self.content_input.setPlaceholderText("Descriptor general de l'alumne…")
        self.layout.addWidget(self.content_input)
        self._add_footer("El contingut no pot estar buit.")

    def value(self):
        """Retorna el contingut del descriptor sense espais sobrants."""
        return self.content_input.toPlainText().strip()

    def _is_valid(self):
        return bool(self.value())
