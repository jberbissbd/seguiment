from types import SimpleNamespace

from PySide6.QtWidgets import QDialog, QFileDialog

from tutopy.models.bulk_import import (
    ImportAction, StudentConflict, StudentImportRow,
)
from tutopy.models.messaging import Student
from tutopy.ui.dialogs.annotation_dialog import AnnotationDialog
from tutopy.ui.dialogs.contact_dialog import ContactDialog
from tutopy.ui.dialogs.document_dialog import DocumentDialog
from tutopy.ui.dialogs.import_conflicts_dialog import ImportConflictsDialog
from tutopy.ui.dialogs.text_value_dialog import TextValueDialog


def test_annotation_dialog_valida_i_normalitza(qtbot):
    dialog = AnnotationDialog()
    qtbot.addWidget(dialog)
    dialog.content_input.setPlainText("   ")
    dialog._accept_valid()
    assert dialog.error_label.isVisible() is False  # encara no s'ha mostrat el diàleg
    assert not dialog.error_label.isHidden()
    dialog.content_input.setPlainText("  Seguiment general  ")
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.value() == "Seguiment general"


def test_annotation_dialog_carrega_valor_existent(qtbot):
    dialog = AnnotationDialog(annotation=SimpleNamespace(content="Descriptor"))
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "Editar descriptor"
    assert dialog.value() == "Descriptor"


def test_contact_dialog_valida_i_retorna_tots_els_camps(qtbot):
    dialog = ContactDialog()
    qtbot.addWidget(dialog)
    dialog._accept_valid()
    assert not dialog.error_label.isHidden()
    dialog.name_input.setText("  Joana  ")
    dialog.description_input.setText("  Mare  ")
    dialog.phone_input.setText("  600 000 000 ")
    dialog.email_input.setText("  joana@example.cat ")
    assert dialog.values() == {
        "name": "Joana", "description": "Mare",
        "phone": "600 000 000", "email": "joana@example.cat",
    }
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_contact_dialog_carrega_contacte(qtbot):
    contact = SimpleNamespace(name="Joan", description="Pare", phone="123", email="a@b.cat")
    dialog = ContactDialog(contact=contact)
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "Editar contacte"
    assert dialog.values()["email"] == "a@b.cat"


def test_document_dialog_selecciona_fitxer_i_dedueix_nom(qtbot, monkeypatch, tmp_path):
    source = tmp_path / "informe.pdf"
    source.write_bytes(b"pdf")
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *args: (str(source), ""))
    dialog = DocumentDialog()
    qtbot.addWidget(dialog)
    dialog._browse()
    assert dialog.values()["source_path"] == str(source)
    assert dialog.values()["name"] == "informe.pdf"
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_document_dialog_no_modifica_res_si_es_cancella(qtbot, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("", ""))
    dialog = DocumentDialog()
    qtbot.addWidget(dialog)
    dialog._browse()
    dialog._accept_valid()
    assert dialog.values()["source_path"] == ""
    assert not dialog.error_label.isHidden()


def test_document_existent_no_requereix_nou_fitxer(qtbot):
    document = SimpleNamespace(name="Informe", description="Final", original_filename="a.pdf")
    dialog = DocumentDialog(document=document)
    qtbot.addWidget(dialog)
    dialog._accept_valid()
    assert dialog.windowTitle() == "Editar document"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_text_value_dialog_valida_i_normalitza(qtbot):
    dialog = TextValueDialog("Categoria", "Nom:", "  Inicial  ")
    qtbot.addWidget(dialog)
    assert dialog.value() == "Inicial"
    dialog.value_input.clear()
    dialog._accept_valid()
    assert not dialog.error_label.isHidden()
    dialog.value_input.setText("  Acadèmic  ")
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.value() == "Acadèmic"


def test_conflictes_permeten_les_tres_decisions(qtbot):
    existing = Student(7, "uuid", "Júlia", "Martínez", "2n A")
    conflict = StudentConflict(
        StudentImportRow(4, "Julia", "Martines", "2n B"), (existing,)
    )
    dialog = ImportConflictsDialog((conflict,))
    qtbot.addWidget(dialog)
    row, action, target = dialog._rows[0]
    assert dialog.decisions()[0].action == ImportAction.CREATE
    action.setCurrentIndex(1)
    assert dialog.decisions()[0].action == ImportAction.SKIP
    assert dialog.decisions()[0].student_id is None
    action.setCurrentIndex(2)
    assert target.isEnabled()
    decision = dialog.decisions()[0]
    assert decision.action == ImportAction.UPDATE
    assert decision.student_id == 7
