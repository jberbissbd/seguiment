from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout,
)
from tutopy.ui.widgets.date_input import DateInput


class DocumentDialog(QDialog):
    def __init__(self, parent=None, document=None):
        super().__init__(parent)
        self.document = document
        self.setWindowTitle("Editar document" if document else "Nou document")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit(document.name if document else "")
        self.description_input = QLineEdit(document.description if document else "")
        saved_date = getattr(document, "date", "") if document else ""
        initial_date = (QDate.fromString(saved_date, "yyyy-MM-dd")
                        if saved_date else QDate.currentDate())
        self.date_input = DateInput(initial_date)
        self.path_input = QLineEdit(document.original_filename if document else "")
        self.path_input.setReadOnly(True)
        browse = QPushButton("Seleccionar…")
        browse.clicked.connect(self._browse)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input, 1)
        path_layout.addWidget(browse)
        form.addRow("Nom:", self.name_input)
        form.addRow("Descripció:", self.description_input)
        form.addRow("Data (DD/MM/AAAA):", self.date_input)
        form.addRow("Fitxer:", path_layout)
        layout.addLayout(form)
        self.error_label = QLabel(
            "Cal indicar un nom, una data vàlida i seleccionar un fitxer."
        )
        self.error_label.setObjectName("errorText")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._accept_valid)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def values(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "source_path": self.path_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
        }

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar document")
        if path:
            self.path_input.setText(path)
            if not self.name_input.text().strip():
                self.name_input.setText(Path(path).name)

    def _accept_valid(self):
        values = self.values()
        path_ok = self.document is not None or bool(values["source_path"])
        if values["name"] and path_ok and self.date_input.date().isValid():
            self.accept()
        else:
            self.error_label.show()
