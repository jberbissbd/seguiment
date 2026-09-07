from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Student
from tutopy.ui.dialogs.bulk_student_edit_dialog import BulkStudentEditDialog


def _students():
    return (
        Student(1, "uuid-1", "Anna", "Serra", "1A"),
        Student(2, "uuid-2", "Biel", "Puig", "1B"),
    )


def test_dialog_aplica_grup_a_files_seleccionades_i_retorna_canvis(qtbot):
    dialog = BulkStudentEditDialog(_students(), ("1A", "1B", "2A"))
    qtbot.addWidget(dialog)
    dialog.table.selectRow(0)
    dialog.group_input.setCurrentText("2A")
    dialog._apply_group()
    dialog.table.item(1, 1).setText("Puig-Soler")
    dialog.change_date.setDate(QDate(2026, 9, 1))

    dialog._accept_valid()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.effective_date() == "2026-09-01"
    assert dialog.changes() == [
        {"student_id": 1, "name": "Anna", "surnames": "Serra", "group_name": "2A"},
        {"student_id": 2, "name": "Biel", "surnames": "Puig-Soler", "group_name": "1B"},
    ]


def test_dialog_no_accepta_un_lot_sense_canvis(qtbot):
    dialog = BulkStudentEditDialog(_students())
    qtbot.addWidget(dialog)

    dialog._accept_valid()

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog.error_label.isVisibleTo(dialog)
