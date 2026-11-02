from unittest.mock import Mock

from tutopy.models.classroom_layout import ClassroomLayout
from tutopy.ui.dialogs.classroom_layout_template_dialog import (
    COLUMNS, DUPLICATE, EXAM, FREE, ISLANDS, U_SHAPE, ClassroomLayoutTemplateDialog,
)

DEFAULTS = {
    "column_pattern": "2-2-2", "teacher_mode": "strip", "teacher_position": "center",
    "leftover_criterion": "back", "fill_order": "rows", "fill_random": False,
    "fill_direction": "left",
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


def test_direccio_nomes_activa_quan_ompliment_es_per_columnes(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    assert dialog.fill_direction_input.isEnabled() is False

    dialog.fill_order_input.setCurrentIndex(dialog.fill_order_input.findData("columns"))
    assert dialog.fill_direction_input.isEnabled() is True
    assert dialog.values()["fill_order"] == "columns"

    dialog.fill_direction_input.setCurrentIndex(dialog.fill_direction_input.findData("right"))
    assert dialog.values()["fill_direction"] == "right"


def test_canviar_a_columnes_actualitza_els_parametres(qtbot):
    dialog = ClassroomLayoutTemplateDialog(26, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("2-3-2")
    values = dialog.values()
    assert values["disposition"] == COLUMNS
    assert values["parameters"]["pattern"] == "2-3-2"
    assert values["parameters"]["block_rows"] is None  # sense marcar, cap bloc fixat


def test_alcada_per_bloc_amagada_fins_que_es_marca(qtbot):
    dialog = ClassroomLayoutTemplateDialog(30, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("2-2-2")
    assert dialog.block_heights_container.isHidden() is True
    assert len(dialog.block_height_inputs) == 3

    dialog.custom_block_heights_checkbox.setChecked(True)
    assert dialog.block_heights_container.isHidden() is False


def test_alcada_per_bloc_es_recalcula_en_canviar_el_patro(qtbot):
    dialog = ClassroomLayoutTemplateDialog(30, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("2-2-2")
    assert len(dialog.block_height_inputs) == 3
    dialog.column_pattern_input.setText("3-3")
    assert len(dialog.block_height_inputs) == 2


def test_alcada_per_bloc_fixa_es_passa_als_parametres(qtbot):
    """Exemple de l'usuari: primer bloc amb 4 files fixes, els altres automàtics."""
    dialog = ClassroomLayoutTemplateDialog(30, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("2-2-2")
    dialog.custom_block_heights_checkbox.setChecked(True)
    dialog.block_height_inputs[0].setValue(4)
    # els blocs 1 i 2 es deixen a "Automàtic" (valor especial 0)

    values = dialog.values()
    assert values["parameters"]["block_rows"] == [4, None, None]


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
    dialog.preview.set_grid = Mock()
    dialog.free_rows_input.setValue(7)
    dialog.preview.set_grid.assert_called()


def test_previsualitzacio_mostra_el_resum_de_seients(qtbot):
    dialog = ClassroomLayoutTemplateDialog(20, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.free_rows_input.setValue(4)
    dialog.free_columns_input.setValue(6)
    # 4x6 = 24 seients per a 20 alumnes: 4 sobrants, amb el criteri "Al fons" per defecte
    assert "20 alumnes" in dialog.preview_summary.text()
    assert "24 seients" in dialog.preview_summary.text()
    assert "4 sobrants" in dialog.preview_summary.text()


def test_previsualitzacio_marca_els_seients_sobrants(qtbot):
    dialog = ClassroomLayoutTemplateDialog(2, [], DEFAULTS)
    qtbot.addWidget(dialog)
    dialog.free_rows_input.setValue(1)
    dialog.free_columns_input.setValue(3)
    # 3 seients per a 2 alumnes, criteri "Al fons": en sobra 1
    assert dialog.preview._leftover_seats == {(0, 2)}


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
