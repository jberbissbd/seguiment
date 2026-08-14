"""Diàleg per resoldre conflictes d'identitat durant una transferència."""

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)

from tutopy.models.transfer import TransferAction, TransferDecision


class TransferConflictsDialog(QDialog):
    """Recull una decisió explícita per cada UUID ja existent."""

    OPTIONS = (
        ("Conservar l’alumne local", TransferAction.KEEP_LOCAL),
        ("Substituir amb les dades importades", TransferAction.REPLACE),
        ("Importar com un alumne nou", TransferAction.IMPORT_AS_NEW),
    )

    def __init__(self, conflicts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conflictes de transferència")
        self.resize(760, 360)
        layout = QVBoxLayout(self)
        label = QLabel(
            "Aquests alumnes ja existeixen. Tria què cal fer amb cadascun."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.table = QTableWidget(len(conflicts), 3)
        self.table.setHorizontalHeaderLabels(
            ["Alumne importat", "Alumne local", "Acció"]
        )
        self._rows = []
        for row, conflict in enumerate(conflicts):
            self.table.setItem(row, 0, QTableWidgetItem(conflict.incoming_name))
            self.table.setItem(row, 1, QTableWidgetItem(conflict.local_name))
            combo = QComboBox()
            for label_text, action in self.OPTIONS:
                combo.addItem(label_text, action)
            self.table.setCellWidget(row, 2, combo)
            self._rows.append((conflict.uuid, combo))
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def decisions(self) -> tuple[TransferDecision, ...]:
        return tuple(
            TransferDecision(student_uuid, combo.currentData())
            for student_uuid, combo in self._rows
        )
