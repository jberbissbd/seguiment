"""Vistes CRUD genèriques (llista i taula) reutilitzades per diverses pestanyes.

Ofereix un patró comú de "crear / editar / eliminar" sobre una `QListWidget`
o una `QTableWidget`, sense conèixer el tipus d'entitat concret: qui les fa
servir només ha de proporcionar les files a mostrar i escoltar els senyals
`create_requested`, `edit_requested` i `delete_requested`.
"""

from collections.abc import Iterable, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from tutopy.ui.resources import set_button_icon


class CrudActions(QWidget):
    """Fila de botons "crear / editar / eliminar" compartida per les vistes CRUD."""

    create_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, create_text: str = "Nou", parent: QWidget | None = None):
        """Crea els tres botons d'acció, amb editar/eliminar deshabilitats.

        Args:
            create_text: Text del botó de creació (p. ex. "Nou alumne").
            parent: Widget pare de Qt.
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.create_button = QPushButton(create_text)
        self.create_button.setObjectName("primaryButton")
        self.edit_button = QPushButton("Editar")
        self.edit_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setObjectName("dangerButton")
        set_button_icon(self.create_button, "add")
        set_button_icon(self.edit_button, "edit")
        set_button_icon(self.delete_button, "delete")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.create_button.clicked.connect(self.create_requested)
        layout.addWidget(self.create_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addStretch()

    def set_selection_enabled(self, enabled: bool) -> None:
        """Activa o desactiva els botons d'editar i eliminar."""
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)


class CrudListView(QWidget):
    """CRUD genèric sobre una `QListWidget` d'una sola columna de text."""

    create_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, create_text: str = "Nou", parent: QWidget | None = None):
        """Munta la capçalera d'accions i la llista, connectant els senyals.

        Args:
            create_text: Text del botó de creació.
            parent: Widget pare de Qt.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.actions = CrudActions(create_text)
        self.list_widget = QListWidget()
        layout.addWidget(self.actions)
        layout.addWidget(self.list_widget, 1)
        self.actions.create_requested.connect(self.create_requested)
        self.actions.edit_button.clicked.connect(self._edit)
        self.actions.delete_button.clicked.connect(self._delete)
        self.list_widget.itemSelectionChanged.connect(self._selection_changed)
        self.list_widget.itemDoubleClicked.connect(
            lambda item: self.edit_requested.emit(item.data(Qt.ItemDataRole.UserRole))
        )

    def set_items(self, items: Iterable[tuple[int, str]]) -> None:
        """Reconstrueix la llista i conserva la selecció si l'ID hi segueix.

        Args:
            items: Iterable de tuples `(id, text)`.
        """
        selected_id = self.current_id()
        self.list_widget.clear()
        for item_id, text in items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, item_id)
            self.list_widget.addItem(item)
            if item_id == selected_id:
                self.list_widget.setCurrentItem(item)
        self._selection_changed()

    def current_id(self):
        """Retorna l'ID de l'element seleccionat, o `None` si no n'hi ha cap."""
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _selection_changed(self):
        self.actions.set_selection_enabled(self.current_id() is not None)

    def _edit(self):
        if self.current_id() is not None:
            self.edit_requested.emit(self.current_id())

    def _delete(self):
        if self.current_id() is not None:
            self.delete_requested.emit(self.current_id())


class CrudTableView(QWidget):
    """CRUD genèric sobre una `QTableWidget` de columnes configurables."""

    create_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(
        self, headers: Sequence[str], create_text: str = "Nou",
        parent: QWidget | None = None,
    ):
        """Munta la capçalera d'accions i la taula, connectant els senyals.

        Args:
            headers: Títols de les columnes de la taula.
            create_text: Text del botó de creació.
            parent: Widget pare de Qt.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.actions = CrudActions(create_text)
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        layout.addWidget(self.actions)
        layout.addWidget(self.table, 1)
        self.actions.create_requested.connect(self.create_requested)
        self.actions.edit_button.clicked.connect(self._edit)
        self.actions.delete_button.clicked.connect(self._delete)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.cellDoubleClicked.connect(
            lambda row, _column: self.edit_requested.emit(self._id_at(row))
        )

    def set_rows(self, rows: Iterable[tuple[int, Sequence]]) -> None:
        """Reconstrueix la taula i conserva la selecció si l'ID hi segueix.

        Args:
            rows: Iterable de tuples `(id, valors_de_columna)`.
        """
        selected_id = self.current_id()
        self.table.setRowCount(0)
        for entity_id, values in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, entity_id)
                self.table.setItem(row, column, item)
            if entity_id == selected_id:
                self.table.selectRow(row)
        self._selection_changed()

    def current_id(self):
        """Retorna l'ID de la fila seleccionada, o `None` si no n'hi ha cap."""
        rows = self.table.selectionModel().selectedRows()
        return self._id_at(rows[0].row()) if rows else None

    def _id_at(self, row):
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _selection_changed(self):
        self.actions.set_selection_enabled(self.current_id() is not None)

    def _edit(self):
        if self.current_id() is not None:
            self.edit_requested.emit(self.current_id())

    def _delete(self):
        if self.current_id() is not None:
            self.delete_requested.emit(self.current_id())
