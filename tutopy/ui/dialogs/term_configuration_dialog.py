"""Diàleg per configurar les dates d'inici dels trimestres d'un curs i grup."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QVBoxLayout,
)

from tutopy.ui.resources import set_dialog_button_icons

from tutopy.ui.widgets.date_input import DateInput


class TermConfigurationDialog(QDialog):
    """Recull el curs, el grup i les dates d'inici del 2n i 3r trimestre."""

    def __init__(self, courses, groups, configuration=None, parent=None):
        """Construeix el diàleg, precarregant les dades si s'edita una configuració existent.

        Args:
            courses: Cursos acadèmics disponibles per seleccionar.
            groups: Noms de grup existents per emplenar el desplegable de grup.
            configuration: Configuració de trimestres existent a editar, o `None`
                per crear-ne una de nova.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent)
        self.setWindowTitle("Configurar trimestres")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.course_input = QComboBox()
        for course in courses:
            self.course_input.addItem(course.course, course.id)
        self.group_input = QComboBox()
        self.group_input.setEditable(True)
        self.group_input.addItems(groups)
        self.second_start = DateInput()
        self.third_start = DateInput()
        form.addRow("Curs acadèmic:", self.course_input)
        form.addRow("Grup:", self.group_input)
        form.addRow("Inici del 2n trimestre:", self.second_start)
        form.addRow("Inici del 3r trimestre:", self.third_start)
        layout.addLayout(form)
        self.error_label = QLabel("Cal seleccionar un curs, un grup i dues dates vàlides.")
        self.error_label.setObjectName("errorText")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        set_dialog_button_icons(buttons)
        buttons.accepted.connect(self._accept_valid)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if configuration is not None:
            self.course_input.setCurrentIndex(
                self.course_input.findData(configuration.academic_course_id)
            )
            self.group_input.setCurrentText(configuration.group_name)
            self.second_start.setDate(QDate.fromString(configuration.second_term_start, "yyyy-MM-dd"))
            self.third_start.setDate(QDate.fromString(configuration.third_term_start, "yyyy-MM-dd"))

    def values(self):
        """Retorna les dades de la configuració de trimestres introduïdes."""
        return {
            "academic_course_id": self.course_input.currentData(),
            "group_name": self.group_input.currentText().strip(),
            "second_term_start": self.second_start.date().toString("yyyy-MM-dd"),
            "third_term_start": self.third_start.date().toString("yyyy-MM-dd"),
        }

    def _accept_valid(self):
        values = self.values()
        if (values["academic_course_id"] is None or not values["group_name"]
                or not self.second_start.date().isValid()
                or not self.third_start.date().isValid()):
            self.error_label.show()
            return
        self.accept()
