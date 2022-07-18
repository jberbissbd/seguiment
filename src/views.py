from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QTableView, QAbstractItemView, QDialog, QDialogButtonBox, QFormLayout, \
    QHBoxLayout, QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableView, QVBoxLayout, QWidget

from model import ContactsModel


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        # Snip...
        self.contactsModel = ContactsModel()
        self.setupUI()

    def setupUI(self):
        """Setup the main window's GUI."""
        # Create the table view widget
        self.table = QTableView()
        self.table.setModel(self.contactsModel.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)


class AddDialog(QDialog):
    """Add Contact dialog."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent=parent)
        self.buttonsBox = None
        self.setWindowTitle("Add Contact")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None
        self.setupUI()

    def setupUI(self):

        """Setup the Add Contact dialog's GUI."""

        # Create line edits for data fields
        self.nameField = QLineEdit()
        self.nameField.setObjectName("Name")
        self.jobField = QLineEdit()
        self.jobField.setObjectName("Job")
        self.emailField = QLineEdit()
        self.emailField.setObjectName("Email")
        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Name:", self.nameField)
        layout.addRow("Job:", self.jobField)
        layout.addRow("Email:", self.emailField)
        self.layout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def accept(self):

        """Accept the data provided through the dialog."""
        self.data = []
        for field in (self.nameField, self.jobField, self.emailField):
            if not field.text():
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"You must provide a contact's {field.objectName()}",
                )
                self.data = None  # Reset .data
                return
            self.data.append(field.text())
        if not self.data:
            return
        super().accept()
