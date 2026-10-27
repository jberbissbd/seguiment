"""Diàleg per triar i previsualitzar una plantilla de disposició abans d'aplicar-la."""

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QSpinBox, QStackedWidget, QVBoxLayout, QWidget,
)

from tutopy.models.classroom_layout import ClassroomLayout
from tutopy.models.classroom_layout_generators import (
    generate_columns, generate_exam, generate_free_grid, generate_islands,
    generate_u_shape,
)
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog
from tutopy.ui.widgets.classroom_layout_grid_widget import ClassroomLayoutGridWidget
from tutopy.ui.widgets.classroom_layout_labels import (
    FILL_ORDER_LABELS, LEFTOVER_LABELS, TEACHER_MODE_LABELS, TEACHER_POSITION_LABELS,
)

FREE = "free"
COLUMNS = "columns"
ISLANDS = "islands"
U_SHAPE = "u_shape"
EXAM = "exam"
DUPLICATE = "duplicate"

DISPOSITION_LABELS = {
    FREE: "Quadrícula lliure",
    COLUMNS: "Agrupacions en columnes",
    ISLANDS: "Grups de treball (illes)",
    U_SHAPE: "En U",
    EXAM: "Examen",
    DUPLICATE: "Duplicar una existent",
}
PREVIEW_MAX_SIZE = 320


class ClassroomLayoutTemplateDialog(BaseFormDialog):
    """Permet triar una disposició, ajustar-ne els paràmetres i previsualitzar-la."""

    def __init__(
        self, student_count: int, other_layouts: list[ClassroomLayout],
        defaults: dict, parent: QWidget | None = None,
    ):
        """Construeix el diàleg, amb els valors inicials de `defaults`.

        Args:
            student_count: Nombre d'alumnes del grup (seients necessaris).
            other_layouts: Altres distribucions del mateix grup, per a
                l'opció "Duplicar una existent".
            defaults: Valors inicials (de `PreferencesService`): patró de
                columnes, mode/posició del professor, criteri de seients
                sobrants i d'ompliment.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent, "Aplicar plantilla")
        self.setMinimumSize(640, 480)
        self.student_count = student_count
        self.other_layouts = other_layouts

        body = QHBoxLayout()
        form_column = QVBoxLayout()

        self.disposition_input = QComboBox()
        for key, label in DISPOSITION_LABELS.items():
            if key == DUPLICATE and not other_layouts:
                continue
            self.disposition_input.addItem(label, key)
        self.disposition_input.currentIndexChanged.connect(self._on_disposition_changed)
        form_column.addWidget(QLabel("Disposició:"))
        form_column.addWidget(self.disposition_input)

        self.parameter_stack = QStackedWidget()
        self._pages: dict[str, int] = {}
        for key in (FREE, COLUMNS, ISLANDS, U_SHAPE, EXAM, DUPLICATE):
            builder = getattr(self, f"_build_{key}_page")
            self._pages[key] = self.parameter_stack.addWidget(builder())
        form_column.addWidget(self.parameter_stack)

        common_form = QFormLayout()
        self.teacher_mode_input = QComboBox()
        for value, label in TEACHER_MODE_LABELS.items():
            self.teacher_mode_input.addItem(label, value)
        self.teacher_position_input = QComboBox()
        for value, label in TEACHER_POSITION_LABELS.items():
            self.teacher_position_input.addItem(label, value)
        self.leftover_input = QComboBox()
        for value, label in LEFTOVER_LABELS.items():
            self.leftover_input.addItem(label, value.value)
        self.fill_order_input = QComboBox()
        for value, label in FILL_ORDER_LABELS.items():
            self.fill_order_input.addItem(label, value.value)
        self.fill_random_input = QCheckBox("Ompliment aleatori (alfabètic si no)")
        common_form.addRow("Taula del professor:", self.teacher_mode_input)
        common_form.addRow("Posició:", self.teacher_position_input)
        common_form.addRow("Seients sobrants:", self.leftover_input)
        common_form.addRow("Ordenar ompliment:", self.fill_order_input)
        common_form.addRow("", self.fill_random_input)
        form_column.addLayout(common_form)
        form_column.addStretch()

        body.addLayout(form_column, 1)

        preview_column = QVBoxLayout()
        preview_column.addWidget(QLabel("Previsualització:"))
        self.preview = ClassroomLayoutGridWidget()
        self.preview.setEnabled(False)
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setMaximumSize(PREVIEW_MAX_SIZE, PREVIEW_MAX_SIZE)
        preview_scroll.setWidget(self.preview)
        preview_column.addWidget(preview_scroll)
        self.preview_error = QLabel("")
        self.preview_error.setObjectName("errorText")
        self.preview_error.setWordWrap(True)
        preview_column.addWidget(self.preview_error)
        preview_column.addStretch()
        body.addLayout(preview_column, 1)

        self.layout.addLayout(body, 1)
        self._add_footer("", save_text="Aplicar")
        self._apply_defaults(defaults)
        self._connect_preview_updates()
        self._on_disposition_changed()

    def _build_free_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.free_rows_input = QSpinBox()
        self.free_rows_input.setRange(1, 20)
        self.free_rows_input.setValue(4)
        self.free_columns_input = QSpinBox()
        self.free_columns_input.setRange(1, 20)
        self.free_columns_input.setValue(6)
        form.addRow("Files:", self.free_rows_input)
        form.addRow("Columnes:", self.free_columns_input)
        return page

    def _build_columns_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.column_pattern_input = QLineEdit()
        self.column_pattern_input.setPlaceholderText('p. ex. "2-3-2"')
        self.aisle_width_input = QSpinBox()
        self.aisle_width_input.setRange(1, 4)
        form.addRow("Patró de columnes:", self.column_pattern_input)
        form.addRow("Amplada del passadís:", self.aisle_width_input)
        return page

    def _build_islands_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.island_rows_input = QSpinBox()
        self.island_rows_input.setRange(1, 6)
        self.island_rows_input.setValue(2)
        self.island_columns_input = QSpinBox()
        self.island_columns_input.setRange(1, 6)
        self.island_columns_input.setValue(2)
        self.islands_per_row_input = QSpinBox()
        self.islands_per_row_input.setRange(1, 10)
        self.islands_per_row_input.setValue(2)
        form.addRow("Files per illa:", self.island_rows_input)
        form.addRow("Columnes per illa:", self.island_columns_input)
        form.addRow("Illes per filera:", self.islands_per_row_input)
        return page

    def _build_u_shape_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.u_shape_auto_input = QCheckBox("Automàtic")
        self.u_shape_auto_input.setChecked(True)
        self.u_shape_seats_input = QSpinBox()
        self.u_shape_seats_input.setRange(2, 20)
        self.u_shape_seats_input.setEnabled(False)
        self.u_shape_auto_input.toggled.connect(
            lambda checked: self.u_shape_seats_input.setEnabled(not checked)
        )
        form.addRow("Seients per costat:", self.u_shape_auto_input)
        form.addRow("", self.u_shape_seats_input)
        return page

    def _build_exam_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.exam_rows_input = QSpinBox()
        self.exam_rows_input.setRange(1, 20)
        self.exam_rows_input.setValue(5)
        self.exam_columns_input = QSpinBox()
        self.exam_columns_input.setRange(1, 20)
        self.exam_columns_input.setValue(6)
        form.addRow("Files:", self.exam_rows_input)
        form.addRow("Columnes:", self.exam_columns_input)
        return page

    def _build_duplicate_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.duplicate_source_input = QComboBox()
        for layout in self.other_layouts:
            self.duplicate_source_input.addItem(layout.name, layout.id)
        form.addRow("Distribució d'origen:", self.duplicate_source_input)
        return page

    def _connect_preview_updates(self) -> None:
        spin_boxes = (
            self.free_rows_input, self.free_columns_input, self.aisle_width_input,
            self.island_rows_input, self.island_columns_input, self.islands_per_row_input,
            self.u_shape_seats_input, self.exam_rows_input, self.exam_columns_input,
        )
        for spin_box in spin_boxes:
            spin_box.valueChanged.connect(self._update_preview)
        self.column_pattern_input.textChanged.connect(self._update_preview)
        self.u_shape_auto_input.toggled.connect(self._update_preview)
        self.duplicate_source_input.currentIndexChanged.connect(self._update_preview)

    def _apply_defaults(self, defaults: dict) -> None:
        self.column_pattern_input.setText(defaults.get("column_pattern", "2-2-2"))
        self.aisle_width_input.setValue(1)
        self.teacher_mode_input.setCurrentIndex(
            self.teacher_mode_input.findData(defaults.get("teacher_mode", "strip"))
        )
        self.teacher_position_input.setCurrentIndex(
            self.teacher_position_input.findData(defaults.get("teacher_position", "center"))
        )
        self.leftover_input.setCurrentIndex(
            self.leftover_input.findData(defaults.get("leftover_criterion", "back"))
        )
        self.fill_order_input.setCurrentIndex(
            self.fill_order_input.findData(defaults.get("fill_order", "rows"))
        )
        self.fill_random_input.setChecked(bool(defaults.get("fill_random", False)))

    def _on_disposition_changed(self, *_args) -> None:
        key = self.disposition_input.currentData()
        self.parameter_stack.setCurrentIndex(self._pages[key])
        self._update_preview()

    def _current_grid(self):
        key = self.disposition_input.currentData()
        if key == FREE:
            return generate_free_grid(
                self.free_rows_input.value(), self.free_columns_input.value(),
            )
        if key == COLUMNS:
            return generate_columns(
                self.column_pattern_input.text().strip(), self.student_count,
                aisle_width=self.aisle_width_input.value(),
            )
        if key == ISLANDS:
            return generate_islands(
                (self.island_rows_input.value(), self.island_columns_input.value()),
                self.islands_per_row_input.value(), self.student_count,
            )
        if key == U_SHAPE:
            seats = None if self.u_shape_auto_input.isChecked() else self.u_shape_seats_input.value()
            return generate_u_shape(seats, self.student_count)
        if key == EXAM:
            return generate_exam(self.exam_rows_input.value(), self.exam_columns_input.value())
        return None  # DUPLICATE: la previsualització no mostra la distribució d'origen

    def _update_preview(self, *_args) -> None:
        self.preview_error.setText("")
        try:
            grid = self._current_grid()
        except ValueError as error:
            self.preview_error.setText(str(error))
            return
        if grid is None:
            return
        self.preview.rebuild(grid, {}, False, {})

    def _is_valid(self) -> bool:
        key = self.disposition_input.currentData()
        if key == COLUMNS:
            try:
                generate_columns(
                    self.column_pattern_input.text().strip(), self.student_count,
                    aisle_width=self.aisle_width_input.value(),
                )
            except ValueError:
                return False
        return True

    def values(self) -> dict:
        """Retorna la disposició triada i tots els seus paràmetres."""
        key = self.disposition_input.currentData()
        parameters: dict = {}
        if key == COLUMNS:
            parameters = {
                "pattern": self.column_pattern_input.text().strip(),
                "aisle_width": self.aisle_width_input.value(),
            }
        elif key == FREE:
            parameters = {
                "rows": self.free_rows_input.value(), "columns": self.free_columns_input.value(),
            }
        elif key == ISLANDS:
            parameters = {
                "island_size": (
                    self.island_rows_input.value(), self.island_columns_input.value(),
                ),
                "islands_per_row": self.islands_per_row_input.value(),
            }
        elif key == U_SHAPE:
            parameters = {
                "seats_per_side": (
                    None if self.u_shape_auto_input.isChecked()
                    else self.u_shape_seats_input.value()
                ),
            }
        elif key == EXAM:
            parameters = {
                "rows": self.exam_rows_input.value(), "columns": self.exam_columns_input.value(),
            }
        elif key == DUPLICATE:
            parameters = {"source_layout_id": self.duplicate_source_input.currentData()}
        return {
            "disposition": key,
            "parameters": parameters,
            "teacher_mode": self.teacher_mode_input.currentData(),
            "teacher_position": self.teacher_position_input.currentData(),
            "leftover_criterion": self.leftover_input.currentData(),
            "fill_order": self.fill_order_input.currentData(),
            "fill_random": self.fill_random_input.isChecked(),
        }
