from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

from tutopy.ui.resources import set_dialog_button_icons


class AnnotationDialog(QDialog):
    def __init__(self, parent=None, annotation=None):
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
        return self.content_input.toPlainText().strip()

    def _accept_valid(self):
        if self.value():
            self.accept()
        else:
            self.error_label.show()
