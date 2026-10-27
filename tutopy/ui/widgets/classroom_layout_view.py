"""Vista de la secció "Distribució d'aula": barra d'eines, pendents i graella.

No conté cap lògica de negoci: emet senyals `*_requested` per a cada acció
de l'usuari i exposa mètodes `set_*`/`rebuild_*` perquè el controlador hi
empenyi l'estat ja preparat.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from tutopy.ui.resources import set_button_icon
from tutopy.ui.widgets.classroom_layout_grid_widget import ClassroomLayoutGridWidget
from tutopy.ui.widgets.classroom_layout_pending_list import PendingStudentsList

TEACHER_MODE_LABELS = {"strip": "Franja", "grid": "Dins la graella"}
TEACHER_POSITION_LABELS = {"left": "Esquerra", "center": "Centre", "right": "Dreta"}


class ClassroomLayoutView(QWidget):
    """Barra d'eines, llista de pendents i graella de la distribució d'aula."""

    group_changed = Signal(str)
    layout_selected = Signal(int)
    new_layout_requested = Signal()
    rows_columns_changed = Signal(int, int)
    teacher_mode_changed = Signal(str)
    teacher_position_changed = Signal(str)
    show_photos_toggled = Signal(bool)
    save_requested = Signal()
    set_active_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        """Construeix la barra d'eines, la llista de pendents i la graella."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._build_toolbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.pending_list = PendingStudentsList()
        self.pending_list.setMinimumWidth(200)
        self.grid_widget = ClassroomLayoutGridWidget()
        grid_container = QWidget()
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.addWidget(self.grid_widget)
        self._teacher_strip_row = QHBoxLayout()
        self.teacher_strip = QLabel("Taula del professor")
        self.teacher_strip.setObjectName("teacherStrip")
        self._teacher_strip_row.addWidget(self.teacher_strip)
        grid_layout.addLayout(self._teacher_strip_row)
        grid_layout.addStretch()
        splitter.addWidget(self.pending_list)
        splitter.addWidget(grid_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter, 1)

    def _build_toolbar(self) -> QFrame:
        toolbar = QFrame()
        toolbar.setObjectName("panel")
        toolbar_layout = QVBoxLayout(toolbar)
        toolbar_layout.setSpacing(10)
        toolbar_layout.addLayout(self._build_selection_row())
        toolbar_layout.addLayout(self._build_grid_settings_row())
        return toolbar

    def _build_selection_row(self) -> QHBoxLayout:
        """Fila 1: quin grup i quina distribució es mostren, i les accions de desar."""
        row = QHBoxLayout()
        row.addWidget(QLabel("Grup:"))
        self.group_input = QComboBox()
        self.group_input.setMinimumWidth(110)
        self.group_input.currentTextChanged.connect(self.group_changed)
        row.addWidget(self.group_input)

        row.addWidget(QLabel("Distribució:"))
        self.layout_input = QComboBox()
        self.layout_input.setMinimumWidth(160)
        self.layout_input.currentIndexChanged.connect(self._emit_layout_selected)
        row.addWidget(self.layout_input, 1)

        self.new_layout_button = QPushButton("Nova…")
        set_button_icon(self.new_layout_button, "add")
        self.new_layout_button.setObjectName("secondaryButton")
        self.new_layout_button.clicked.connect(self.new_layout_requested)
        row.addWidget(self.new_layout_button)

        self.set_active_button = QPushButton("Marcar com a activa")
        set_button_icon(self.set_active_button, "select")
        self.set_active_button.setObjectName("secondaryButton")
        self.set_active_button.clicked.connect(self.set_active_requested)
        row.addWidget(self.set_active_button)

        self.save_button = QPushButton("Desar")
        set_button_icon(self.save_button, "save")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_requested)
        row.addWidget(self.save_button)

        for button in (self.new_layout_button, self.set_active_button, self.save_button):
            button.setMinimumHeight(32)
            button.setMinimumWidth(button.sizeHint().width())
            button.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
            )
        return row

    def _build_grid_settings_row(self) -> QHBoxLayout:
        """Fila 2: mides de la graella, taula del professor i mostrar fotos."""
        row = QHBoxLayout()
        row.addWidget(QLabel("Files:"))
        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 20)
        self.rows_input.setMinimumWidth(56)
        self.rows_input.valueChanged.connect(self._emit_rows_columns)
        row.addWidget(self.rows_input)

        row.addWidget(QLabel("Columnes:"))
        self.columns_input = QSpinBox()
        self.columns_input.setRange(1, 20)
        self.columns_input.setMinimumWidth(56)
        self.columns_input.valueChanged.connect(self._emit_rows_columns)
        row.addWidget(self.columns_input)

        row.addSpacing(12)
        row.addWidget(QLabel("Taula del professor:"))
        self.teacher_mode_input = QComboBox()
        self.teacher_mode_input.setMinimumWidth(140)
        for value, label in TEACHER_MODE_LABELS.items():
            self.teacher_mode_input.addItem(label, value)
        self.teacher_mode_input.currentIndexChanged.connect(
            lambda _index: self.teacher_mode_changed.emit(self.teacher_mode_input.currentData())
        )
        row.addWidget(self.teacher_mode_input)

        self.teacher_position_input = QComboBox()
        self.teacher_position_input.setMinimumWidth(100)
        for value, label in TEACHER_POSITION_LABELS.items():
            self.teacher_position_input.addItem(label, value)
        self.teacher_position_input.currentIndexChanged.connect(
            lambda _index: self.teacher_position_changed.emit(
                self.teacher_position_input.currentData()
            )
        )
        row.addWidget(self.teacher_position_input)

        row.addSpacing(12)
        self.show_photos_checkbox = QCheckBox("Mostrar fotos")
        self.show_photos_checkbox.toggled.connect(self.show_photos_toggled)
        row.addWidget(self.show_photos_checkbox)

        row.addStretch()
        return row

    def set_groups(self, groups: list[str], current: str | None = None) -> None:
        """Omple el desplegable de grups, sense retornar a emetre `group_changed`."""
        self.group_input.blockSignals(True)
        self.group_input.clear()
        self.group_input.addItems(groups)
        if current is not None and current in groups:
            self.group_input.setCurrentText(current)
        self.group_input.blockSignals(False)

    def set_current_group(self, group_name: str | None) -> None:
        """Torna a seleccionar `group_name` sense reemetre `group_changed`."""
        self.group_input.blockSignals(True)
        self.group_input.setCurrentText(group_name or "")
        self.group_input.blockSignals(False)

    def set_layouts(self, layouts: list[tuple[int, str, bool]], current_id: int | None) -> None:
        """Omple el desplegable de distribucions: `(id, nom, és_activa)`."""
        self.layout_input.blockSignals(True)
        self.layout_input.clear()
        for layout_id, name, is_active in layouts:
            label = f"{name} ★" if is_active else name
            self.layout_input.addItem(label, layout_id)
        if current_id is not None:
            index = self.layout_input.findData(current_id)
            if index >= 0:
                self.layout_input.setCurrentIndex(index)
        self.layout_input.blockSignals(False)

    def set_layout_fields(
        self, rows: int, columns: int, teacher_mode: str, teacher_position: str,
        show_photos: bool,
    ) -> None:
        """Mostra els valors de la distribució actual a la barra d'eines."""
        for widget, value in (
            (self.rows_input, rows), (self.columns_input, columns),
        ):
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)
        self.teacher_mode_input.blockSignals(True)
        self.teacher_mode_input.setCurrentIndex(self.teacher_mode_input.findData(teacher_mode))
        self.teacher_mode_input.blockSignals(False)
        self.teacher_position_input.blockSignals(True)
        self.teacher_position_input.setCurrentIndex(
            self.teacher_position_input.findData(teacher_position)
        )
        self.teacher_position_input.blockSignals(False)
        self.show_photos_checkbox.blockSignals(True)
        self.show_photos_checkbox.setChecked(show_photos)
        self.show_photos_checkbox.blockSignals(False)
        self.teacher_position_input.setVisible(teacher_mode == "strip")
        self.set_teacher_strip(teacher_mode == "strip", teacher_position)

    def set_teacher_strip(self, visible: bool, position: str) -> None:
        """Mostra o amaga la franja del professor, alineada segons `position`."""
        self.teacher_strip.setVisible(visible)
        row = self._teacher_strip_row
        while row.count():
            row.takeAt(0)
        if position != "left":
            row.addStretch()
        row.addWidget(self.teacher_strip)
        if position != "right":
            row.addStretch()

    def set_dirty(self, dirty: bool) -> None:
        """Mostra un asterisc al botó de desar quan hi ha canvis pendents."""
        self.save_button.setText("Desar ✱" if dirty else "Desar")

    def _emit_layout_selected(self, _index: int) -> None:
        layout_id = self.layout_input.currentData()
        if layout_id is not None:
            self.layout_selected.emit(layout_id)

    def _emit_rows_columns(self, _value: int) -> None:
        self.rows_columns_changed.emit(self.rows_input.value(), self.columns_input.value())
