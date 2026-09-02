"""Panell reutilitzable per cercar i marcar alumnes d'una llista.

Compartit pels diàlegs que necessiten seleccionar diversos alumnes alhora
(`BatchExportDialog`, `TransferStudentSelectionDialog`): un camp de cerca
amb `debounce`, botons "Seleccionar visibles"/"Desmarcar tots", una
etiqueta amb el recompte i la llista marcable pròpiament dita.
"""

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout, QWidget,
)

from tutopy.models.messaging import Student
from tutopy.ui.resources import set_button_icon
from tutopy.ui.widgets.debounced_line_edit import DebouncedLineEdit


class CheckableStudentListPanel(QWidget):
    """Llista d'alumnes marcables amb cerca, comuna a diversos diàlegs de selecció."""

    def __init__(
        self, students: Sequence[Student],
        item_text: Callable[[Student], str],
        search_key: Callable[[Student], str],
        parent: QWidget | None = None,
    ):
        """Construeix el panell amb els alumnes donats.

        Args:
            students: Alumnes marcables, amb cerca pel text que retorni `search_key`.
            item_text: Text a mostrar per a cada alumne a la llista.
            search_key: Text (normalment en minúscules) contra el qual es filtra.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = DebouncedLineEdit()
        self.search_input.setPlaceholderText("Cercar per nom, cognoms o grup…")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)

        actions = QHBoxLayout()
        self.select_visible_button = QPushButton("Seleccionar visibles")
        self.clear_button = QPushButton("Desmarcar tots")
        set_button_icon(self.select_visible_button, "select")
        set_button_icon(self.clear_button, "deselect")
        self.selection_label = QLabel("0 alumnes seleccionats")
        actions.addWidget(self.select_visible_button)
        actions.addWidget(self.clear_button)
        actions.addStretch()
        actions.addWidget(self.selection_label)
        layout.addLayout(actions)

        self.student_list = QListWidget()
        for student in students:
            item = QListWidgetItem(item_text(student))
            item.setData(Qt.ItemDataRole.UserRole, student.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, search_key(student))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.student_list.addItem(item)
        layout.addWidget(self.student_list, 1)

        self.search_input.debounced_text_changed.connect(self._filter_students)
        self.select_visible_button.clicked.connect(self.select_visible)
        self.clear_button.clicked.connect(self._clear_selection)
        self.student_list.itemChanged.connect(self._update_selection_label)

    def student_ids(self) -> list[int]:
        """Retorna els identificadors marcats en l'ordre visible."""
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for row in range(self.student_list.count())
            if (item := self.student_list.item(row)).checkState()
            == Qt.CheckState.Checked
        ]

    def _filter_students(self, query: str) -> None:
        query = query.strip().casefold()
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            item.setHidden(query not in item.data(Qt.ItemDataRole.UserRole + 1))

    def select_visible(self) -> None:
        """Marca tots els alumnes actualment visibles (no filtrats per la cerca)."""
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)

    def _clear_selection(self) -> None:
        for row in range(self.student_list.count()):
            self.student_list.item(row).setCheckState(Qt.CheckState.Unchecked)

    def _update_selection_label(self, _item=None) -> None:
        self.selection_label.setText(f"{len(self.student_ids())} alumnes seleccionats")
