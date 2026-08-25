from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Student
from tutopy.ui.dialogs.transfer_student_selection_dialog import (
    TransferStudentSelectionDialog,
)


def test_mostra_nom_i_grup_i_permet_seleccio_multiple(qtbot):
    students = [
        Student(1, "u1", "Laia", "Martí", "4t A"),
        Student(2, "u2", "Pau", "Puig", ""),
    ]
    dialog = TransferStudentSelectionDialog(students)
    qtbot.addWidget(dialog)

    assert dialog.student_list.item(0).text() == "Laia Martí — Grup: 4t A"
    assert dialog.student_list.item(1).text() == "Pau Puig — Grup: Sense grup"
    dialog.student_list.item(0).setCheckState(Qt.CheckState.Checked)
    dialog.student_list.item(1).setCheckState(Qt.CheckState.Checked)
    assert dialog.student_ids() == [1, 2]
    assert dialog.selection_label.text() == "2 alumnes seleccionats"


def test_filtra_per_grup_i_exigeix_una_seleccio(qtbot):
    students = [
        Student(1, "u1", "Laia", "Martí", "4t A"),
        Student(2, "u2", "Pau", "Puig", "3r B"),
    ]
    dialog = TransferStudentSelectionDialog(students)
    qtbot.addWidget(dialog)

    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Rejected
    assert not dialog.validation_label.isHidden()
    with qtbot.waitSignal(dialog.search_input.debounced_text_changed, timeout=1_000):
        dialog.search_input.setText("3r B")
    dialog._select_visible()
    assert dialog.student_ids() == [2]
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted
