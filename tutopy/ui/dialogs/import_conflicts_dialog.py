"""Diàleg per resoldre possibles alumnes duplicats durant una importació massiva."""

from collections.abc import Sequence

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QGridLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget,
)

from tutopy.ui.resources import set_dialog_button_icons

from tutopy.models.bulk_import import ImportAction, ImportDecision, StudentConflict


class ImportConflictsDialog(QDialog):
    """Recull una decisió per cada nom similar trobat durant la importació."""

    def __init__(
        self, conflicts: Sequence[StudentConflict], parent: QWidget | None = None
    ):
        """Construeix una fila d'acció per cada conflicte detectat.

        Args:
            conflicts: Conflictes trobats entre les files importades i alumnes existents.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent)
        self.setWindowTitle("Revisar possibles alumnes duplicats")
        self.resize(760, 420)
        self._rows = []
        layout = QVBoxLayout(self)
        intro = QLabel(
            "S’han trobat noms similars. Decideix què cal fer amb cada fila; "
            "cap alumne s’unirà automàticament."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        container = QWidget()
        grid = QGridLayout(container)
        for column, text in enumerate(("Fila", "Alumne del full", "Acció", "Alumne existent")):
            header = QLabel(text)
            header.setStyleSheet("font-weight: 600")
            grid.addWidget(header, 0, column)
        for index, conflict in enumerate(conflicts, 1):
            action = QComboBox()
            action.addItem("Crear com a alumne nou", ImportAction.CREATE)
            action.addItem("Ometre aquesta fila", ImportAction.SKIP)
            action.addItem("Actualitzar l’alumne existent", ImportAction.UPDATE)
            target = QComboBox()
            for student in conflict.matches:
                meta = f" — {student.group_name}" if student.group_name else ""
                target.addItem(f"{student.full_name}{meta}", student.id)
            target.setEnabled(False)
            action.currentIndexChanged.connect(
                lambda _index, a=action, t=target:
                t.setEnabled(a.currentData() == ImportAction.UPDATE)
            )
            grid.addWidget(QLabel(str(conflict.row.row)), index, 0)
            grid.addWidget(QLabel(conflict.row.full_name), index, 1)
            grid.addWidget(action, index, 2)
            grid.addWidget(target, index, 3)
            self._rows.append((conflict.row.row, action, target))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        set_dialog_button_icons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def decisions(self) -> tuple[ImportDecision, ...]:
        """Retorna la decisió triada per a cada fila conflictiva."""
        return tuple(
            ImportDecision(row, action.currentData(),
                           target.currentData() if action.currentData() == ImportAction.UPDATE else None)
            for row, action, target in self._rows
        )
