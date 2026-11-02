from tutopy.ui.dialogs.classroom_layout_dialog import ClassroomLayoutDialog
from tutopy.ui.dialogs.classroom_layout_template_dialog import COLUMNS, FREE


def test_values_inclouen_grup_nom_i_opcions_de_plantilla(qtbot):
    dialog = ClassroomLayoutDialog("1r A", 20, [], {})
    qtbot.addWidget(dialog)
    dialog.name_input.setText("1r trimestre")
    values = dialog.values()
    assert values["group_name"] == "1r A"
    assert values["name"] == "1r trimestre"
    assert values["disposition"] == FREE
    assert "fill_order" in values and "leftover_criterion" in values


def test_sense_nom_mostra_error_i_no_accepta(qtbot):
    dialog = ClassroomLayoutDialog("1r A", 20, [], {})
    qtbot.addWidget(dialog)
    dialog._accept_valid()
    assert not dialog.error_label.isHidden()
    assert "nom" in dialog.error_label.text().lower()
    assert dialog.result() == 0


def test_amb_nom_pero_patro_de_columnes_invalid_tambe_mostra_error(qtbot):
    dialog = ClassroomLayoutDialog("1r A", 20, [], {})
    qtbot.addWidget(dialog)
    dialog.name_input.setText("Nova")
    dialog.disposition_input.setCurrentIndex(dialog.disposition_input.findData(COLUMNS))
    dialog.column_pattern_input.setText("invalid")
    dialog._accept_valid()
    assert not dialog.error_label.isHidden()
    assert dialog.result() == 0


def test_amb_nom_i_dades_valides_accepta(qtbot):
    dialog = ClassroomLayoutDialog("1r A", 20, [], {})
    qtbot.addWidget(dialog)
    dialog.name_input.setText("Nova")
    dialog._accept_valid()
    assert dialog.result() == 1
