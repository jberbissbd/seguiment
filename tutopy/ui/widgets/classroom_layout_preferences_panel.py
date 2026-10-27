"""Panell de preferències per defecte de les plantilles de distribució d'aula."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QFrame, QLabel, QLineEdit, QVBoxLayout,
)

from tutopy.ui.widgets.classroom_layout_labels import (
    FILL_ORDER_LABELS, LEFTOVER_LABELS, TEACHER_MODE_LABELS, TEACHER_POSITION_LABELS,
)


class ClassroomLayoutPreferencesPanel(QFrame):
    """Valors amb què comença cada distribució/plantilla nova.

    No conté cap lògica de negoci: emet un senyal per camp quan l'usuari
    el canvia, i exposa un `set_*` per camp perquè el controlador hi
    empenyi l'estat ja desat.
    """

    column_pattern_changed = Signal(str)
    teacher_mode_changed = Signal(str)
    teacher_position_changed = Signal(str)
    leftover_criterion_changed = Signal(str)
    fill_order_changed = Signal(str)
    fill_random_changed = Signal(bool)

    def __init__(self, parent=None):
        """Construeix els camps de preferències de distribució d'aula."""
        super().__init__(parent)
        self.setObjectName("panel")
        layout = QVBoxLayout(self)
        title = QLabel("Preferències de distribució d'aula")
        title.setObjectName("studentName")
        layout.addWidget(title)

        form = QFormLayout()
        self.column_pattern_input = QLineEdit()
        self.column_pattern_input.setPlaceholderText('p. ex. "2-2-2"')
        self.column_pattern_input.editingFinished.connect(
            lambda: self.column_pattern_changed.emit(self.column_pattern_input.text().strip())
        )
        form.addRow("Patró de columnes per defecte:", self.column_pattern_input)

        self.teacher_mode_input = QComboBox()
        for value, label in TEACHER_MODE_LABELS.items():
            self.teacher_mode_input.addItem(label, value)
        self.teacher_mode_input.currentIndexChanged.connect(
            lambda _index: self.teacher_mode_changed.emit(self.teacher_mode_input.currentData())
        )
        form.addRow("Taula del professor per defecte:", self.teacher_mode_input)

        self.teacher_position_input = QComboBox()
        for value, label in TEACHER_POSITION_LABELS.items():
            self.teacher_position_input.addItem(label, value)
        self.teacher_position_input.currentIndexChanged.connect(
            lambda _index: self.teacher_position_changed.emit(
                self.teacher_position_input.currentData()
            )
        )
        form.addRow("Posició per defecte:", self.teacher_position_input)

        self.leftover_input = QComboBox()
        for value, label in LEFTOVER_LABELS.items():
            self.leftover_input.addItem(label, value.value)
        self.leftover_input.currentIndexChanged.connect(
            lambda _index: self.leftover_criterion_changed.emit(self.leftover_input.currentData())
        )
        form.addRow("Seients sobrants per defecte:", self.leftover_input)

        self.fill_order_input = QComboBox()
        for value, label in FILL_ORDER_LABELS.items():
            self.fill_order_input.addItem(label, value.value)
        self.fill_order_input.currentIndexChanged.connect(
            lambda _index: self.fill_order_changed.emit(self.fill_order_input.currentData())
        )
        form.addRow("Ordenar ompliment per defecte:", self.fill_order_input)

        self.fill_random_input = QCheckBox("Ompliment aleatori per defecte (alfabètic si no)")
        self.fill_random_input.toggled.connect(self.fill_random_changed)
        form.addRow("", self.fill_random_input)

        layout.addLayout(form)

    def set_values(
        self, column_pattern: str, teacher_mode: str, teacher_position: str,
        leftover_criterion: str, fill_order: str, fill_random: bool,
    ) -> None:
        """Mostra els valors actuals sense reemetre cap senyal de canvi."""
        self.column_pattern_input.blockSignals(True)
        self.column_pattern_input.setText(column_pattern)
        self.column_pattern_input.blockSignals(False)
        for combo, value in (
            (self.teacher_mode_input, teacher_mode),
            (self.teacher_position_input, teacher_position),
            (self.leftover_input, leftover_criterion),
            (self.fill_order_input, fill_order),
        ):
            combo.blockSignals(True)
            combo.setCurrentIndex(combo.findData(value))
            combo.blockSignals(False)
        self.fill_random_input.blockSignals(True)
        self.fill_random_input.setChecked(fill_random)
        self.fill_random_input.blockSignals(False)
