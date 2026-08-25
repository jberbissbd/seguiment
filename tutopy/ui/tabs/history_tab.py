"""Pestanya d'històric de grups i cursos de l'alumne (només lectura)."""

from collections.abc import Iterable

from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class HistoryTab(QWidget):
    """Taula de només lectura amb l'històric de grups i cursos de l'alumne."""

    def __init__(self, parent=None):
        """Construeix la taula d'històric (Grup, Curs, Inici, Final)."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Grup", "Curs", "Inici", "Final"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def set_history(self, rows: Iterable[tuple[str, str, str, str]]) -> None:
        """Omple la taula amb l'històric de grups i cursos.

        Args:
            rows: Iterable de tuples `(grup, curs, inici, final)`.
        """
        self.table.setRowCount(0)
        for values in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
