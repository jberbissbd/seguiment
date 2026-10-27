from unittest.mock import Mock

from tutopy.models.classroom_layout import ClassroomLayout
from tutopy.ui.dialogs.classroom_layout_template_dialog import (
    COLUMNS, DUPLICATE, EXAM, FREE, ISLANDS, U_SHAPE, ClassroomLayoutTemplateDialog,
)

DEFAULTS = {
    "column_pattern": "2-2-2", "teacher_mode": "strip", "teacher_position": "center",
    "leftover_criterion": "back", "fill_order": "rows", "fill_random": False,
}


def _other_layout(layout_id=1, name="A1"):
    return ClassroomLayout(
        layout_id, "4t A", name, 3, 4, "strip", "center", False, False,
        "2026-01-01", "2026-01-01",
    )


def test_disposicio_per_defecte_es_quadricula_lliure(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    assert dialog.disposition_input.currentData() == FREE
    assert dialog.values()["disposition"] == FREE


def test_valors_inicials_vénen_de_les_preferencies(qtbot):
    defaults = dict(DEFAULTS, column_pattern="3-3", teacher_mode="grid", fill_random=True)
    dialog = ClassroomLayoutTemplateDialog(20, [], defaults)
    qtbot.addWidget(dialog)
    assert dialog.column_pattern_input.text() == "3-3"
    assert dialog.teacher_mode_input.currentData() == "grid"
    assert dialog.fill_random_input.isChecked() is True


def test_canviar_a_columnes_actualitza_els_parametres(qtbot):
    dialog = ClassroomLayoutTemplateDialog(26, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("2-3-2")
    values = dialog.values()
    assert values["disposition"] == COLUMNS
    assert values["parameters"]["pattern"] == "2-3-2"


def test_patro_invalid_mostra_error_de_previsualitzacio_i_invalida(qtbot):
    dialog = ClassroomLayoutTemplateDialog(10, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("no-es-un-patro-valid")
    assert dialog.preview_error.text() != ""
    assert dialog._is_valid() is False


def test_previsualitzacio_es_recalcula_en_canviar_parametres(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.preview.rebuild = Mock()
    dialog.free_rows_input.setValue(7)
    dialog.preview.rebuild.assert_called()


def test_illes_parametres(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(ISLANDS))
    dialog.island_rows_input.setValue(2)
    dialog.island_columns_input.setValue(3)
    dialog.islands_per_row_input.setValue(4)
    values = dialog.values()
    assert values["parameters"] == {"island_size": (2, 3), "islands_per_row": 4}


def test_u_automatic_per_defecte(qtbot):
    dialog = ClassroomLayoutTemplateDialog(12, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(U_SHAPE))
    assert dialog.values()["parameters"]["seats_per_side"] is None
    dialog.u_shape_auto_input.setChecked(False)
    dialog.u_shape_seats_input.setValue(5)
    assert dialog.values()["parameters"]["seats_per_side"] == 5


def test_examen_parametres(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(EXAM))
    dialog.exam_rows_input.setValue(5)
    dialog.exam_columns_input.setValue(6)
    assert dialog.values()["parameters"] == {"rows": 5, "columns": 6}


def test_duplicar_nomes_disponible_amb_altres_distribucions(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    assert dialog.disposition_input.findData(DUPLICATE) == -1

    other = [_other_layout(5, "A2")]
    dialog2 = ClassroomLayoutTemplateDialog(20, other, DEFAULTS)
    qtbot.addWidget(dialog2)
    index = dialog2.disposition_input.findData(DUPLICATE)
    assert index != -1
    dialog2.disposition_input.setCurrentIndex(index)
    assert dialog2.values()["parameters"]["source_layout_id"] == 5
