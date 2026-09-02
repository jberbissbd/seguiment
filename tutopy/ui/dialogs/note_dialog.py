"""Diàleg per crear o editar una nota de seguiment d'un alumne."""

from collections.abc import Sequence

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QFormLayout, QPlainTextEdit, QWidget

from tutopy.models.messaging import Category, Note
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog

from tutopy.ui.widgets.date_input import DateInput


class NoteDialog(BaseFormDialog):
    """Recull una nota de seguiment sense accedir als serveis."""

    def __init__(
        self, parent: QWidget | None = None, note: Note | None = None,
        student_id: int | None = None, categories: Sequence[Category] = (),
    ):
        """Construeix el diàleg, precarregant les dades si s'edita una nota existent.

        Args:
            parent: Widget pare de Qt, si escau.
            note: Nota existent a editar, o `None` per crear-ne una de nova.
            student_id: Identificador de l'alumne al qual pertany la nota nova.
            categories: Categories disponibles per classificar la nota.
        """
        super().__init__(parent, "Editar nota" if note else "Nova nota")
        self.student_id = note.student_id if note else student_id
        self.setModal(True)
        self.setMinimumWidth(520)

        form = QFormLayout()
        self.category_input = QComboBox()
        for category in categories:
            self.category_input.addItem(category.name, category.id)
        self.date_input = DateInput(QDate.currentDate())
        self.date_input.setToolTip(
            "Escriu la data en format DD/MM/AAAA o selecciona-la al calendari."
        )
        self.date_input.setAccessibleName("Data de la nota")
        self.date_input.setAccessibleDescription(
            "Data editable en format DD/MM/AAAA amb calendari emergent"
        )
        self.content_input = QPlainTextEdit()
        self.content_input.setPlaceholderText("Contingut de la nota de seguiment…")
        form.addRow("Categoria:", self.category_input)
        form.addRow("Data (DD/MM/AAAA):", self.date_input)
        form.addRow("Contingut:", self.content_input)
        self.layout.addLayout(form)
        self._add_footer("")

        if note:
            self._select_data(self.category_input, note.category_id)
            self.date_input.setDate(QDate.fromString(note.date, "yyyy-MM-dd"))
            self.content_input.setPlainText(note.content)

    def values(self) -> dict:
        """Retorna les dades de la nota introduïdes, llestes per desar."""
        return {
            "student_id": self.student_id,
            "category_id": self.category_input.currentData(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "course_id": 0,
            "content": self.content_input.toPlainText().strip(),
        }

    def _accept_valid(self) -> None:
        values = self.values()
        if values["student_id"] is None:
            self._show_error("No hi ha cap alumne seleccionat.")
        elif values["category_id"] is None:
            self._show_error("Cal seleccionar una categoria.")
        elif not self.date_input.date().isValid():
            self._show_error("La data ha de tenir el format DD/MM/AAAA.")
        elif not values["content"]:
            self._show_error("El contingut no pot estar buit.")
        else:
            self.accept()

    @staticmethod
    def _select_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)
