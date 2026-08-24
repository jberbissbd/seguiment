from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Category, Student
from tutopy.ui.dialogs.batch_export_dialog import BatchExportDialog


def test_selecciona_alumnes_visibles_i_conserva_els_ocults(qtbot):
    students = [
        Student(1, "u1", "Laia", "Martí", "4t A"),
        Student(2, "u2", "Pau", "Puig", "3r B"),
    ]
    dialog = BatchExportDialog(students, [Category(1, "Acadèmic")])
    qtbot.addWidget(dialog)
    dialog.student_list.item(1).setCheckState(Qt.CheckState.Checked)
    with qtbot.waitSignal(dialog.search_input.debounced_text_changed, timeout=1_000):
        dialog.search_input.setText("Laia")
    dialog._select_visible()
    assert dialog.student_ids() == [1, 2]
    assert dialog.selection_label.text() == "2 alumnes seleccionats"


def test_requereix_seleccio_i_retorna_opcions(qtbot):
    student = Student(1, "u1", "Laia", "Martí", "4t A")
    dialog = BatchExportDialog([student], [Category(3, "Família")])
    qtbot.addWidget(dialog)
    dialog._accept_valid()
    assert dialog.result() == 0
    assert not dialog.validation_label.isHidden()
    dialog.student_list.item(0).setCheckState(Qt.CheckState.Checked)
    dialog.format_input.setCurrentIndex(1)
    dialog.include_documents.setChecked(True)
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.student_ids() == [1]
    assert dialog.category_order() == [3]
    assert dialog.export_format() == "docx"
    assert not dialog.include_terms.isEnabled()
