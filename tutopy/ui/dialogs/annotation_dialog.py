"""Diàleg per crear o editar un descriptor general d'un alumne."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

from tutopy.ui.resources import set_dialog_button_icons


class AnnotationDialog(QDialog):
    """Recull el text d'un descriptor general, nou o existent."""

    def __init__(self, parent=None, annotation=None):
        """Construeix el diàleg, precarregant el contingut si s'edita un descriptor existent.

        Args:
            parent: Widget pare de Qt, si escau.
            annotation: Descriptor existent a editar, o `None` per crear-ne un de nou.
        """
        super().__init__(parent)
        self.setWindowTitle("Editar descriptor" if annotation else "Nou descriptor")
        layout = QVBoxLayout(self)
        self.content_input = QPlainTextEdit(annotation.content if annotation else "")
        self.content_input.setPlaceholderText("Descriptor general de l'alumne…")
        layout.addWidget(self.content_input)
        self.error_label = QLabel("El contingut no pot estar buit.")
        self.error_label.setObjectName("errorText")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        set_dialog_button_icons(self.buttons)
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def value(self):
        """Retorna el contingut del descriptor sense espais sobrants."""
        return self.content_input.toPlainText().strip()

    def _accept_valid(self):
        if self.value():
            self.accept()
        else:
            self.error_label.show()
