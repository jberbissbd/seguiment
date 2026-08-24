from PySide6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from tutopy.application import create_services
from tutopy.controllers.student_controller import StudentController
from tutopy.database.database import Database
from tutopy.models.messaging import StudentNew
from tutopy.ui.dialogs.student_dialog import StudentDialog
from tutopy.ui.main_window import MainWindow


class AcceptedDialog:
    values_to_return = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def exec(self):
        return QDialog.DialogCode.Accepted

    def values(self):
        return dict(self.values_to_return)


def build_controller(qtbot, tmp_path, dialog_factory=AcceptedDialog,
    confirm_delete=lambda _name: True):
    database = Database(str(tmp_path / "crud.db")).connect()
    services = create_services(database)
    window = MainWindow()
    qtbot.addWidget(window)
    errors = []
    controller = StudentController(
        window,
        services.students,
        dialog_factory=dialog_factory,
        confirm_delete=confirm_delete,
        error_handler=errors.append,
    )
    controller.start()
    return database, services, window, controller, errors


def test_student_dialog_valida_i_retorna_valors(qtbot):
    dialog = StudentDialog(groups=["1r A", "2n B"])
    qtbot.addWidget(dialog)
    dialog.name_input.setText("  Jordi ")
    dialog.surnames_input.setText(" Garcia ")
    dialog.group_input.setCurrentText("2n B")

    dialog._validate_and_accept()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.values() == {
        "name": "Jordi", "surnames": "Garcia", "group_name": "2n B"
    }
    assert dialog.group_input.isEditable()
    assert dialog.group_input.count() == 2
    assert not dialog.group_selector_button.isHidden()


def test_student_dialog_no_accepta_camps_obligatoris_buits(qtbot):
    dialog = StudentDialog()
    qtbot.addWidget(dialog)

    dialog.buttons.button(QDialogButtonBox.StandardButton.Save).click()

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert not dialog.validation_label.isHidden()


def test_controller_crea_i_selecciona_alumne(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(AcceptedDialog, "values_to_return", {
        "name": "Jordi", "surnames": "Garcia", "group_name": "4t A"
    })
    database, services, window, controller, errors = build_controller(qtbot, tmp_path)
    try:
        controller.create()

        students = services.students.get_all()
        assert len(students) == 1
        assert window.student_list.current_student_id() == students[0].id
        assert window.student_detail.name_value.text() == "Jordi Garcia"
        assert window.student_detail.avatar_value.text() == "JG"
        assert not hasattr(window.student_detail, "uuid_value")
        assert errors == []
    finally:
        database.close()


def test_controller_edita_alumne_i_grup(qtbot, tmp_path, monkeypatch):
    database, services, window, controller, errors = build_controller(qtbot, tmp_path)
    try:
        student = services.students.create(StudentNew("Jordi", "Garcia", "3r A"))
        monkeypatch.setattr(AcceptedDialog, "values_to_return", {
            "name": "Jordi", "surnames": "Serra", "group_name": "4t B"
        })

        controller.edit(student.id)

        updated = services.students.get_by_id(student.id)
        assert updated.surnames == "Serra"
        assert updated.group_name == "4t B"
        assert services.students.get_current_group(student.id) == "4t B"
        assert window.student_detail.group_value.text() == "4t B"
        assert errors == []
    finally:
        database.close()


def test_controller_elimina_amb_confirmacio(qtbot, tmp_path):
    database, services, window, controller, errors = build_controller(qtbot, tmp_path)
    try:
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        controller.refresh()

        controller.delete(student.id)

        assert services.students.get_all() == []
        assert window.student_list.list_widget.count() == 0
        assert errors == []
    finally:
        database.close()


def test_controller_respecta_cancel_lacio_eliminacio(qtbot, tmp_path):
    database, services, window, controller, errors = build_controller(
        qtbot, tmp_path, confirm_delete=lambda _name: False
    )
    try:
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))

        controller.delete(student.id)

        assert services.students.get_by_id(student.id) is not None
    finally:
        database.close()


def test_controller_aplica_edicio_massiva_en_segon_pla(
    qtbot, tmp_path, monkeypatch
):
    database, services, window, controller, errors = build_controller(qtbot, tmp_path)
    try:
        first = services.students.create(StudentNew("Anna", "Serra", "1A"))
        second = services.students.create(StudentNew("Biel", "Puig", "1B"))

        class AcceptedBulkDialog:
            def __init__(self, students, groups, parent=None):
                assert {item.id for item in students} == {first.id, second.id}

            def exec(self):
                return QDialog.DialogCode.Accepted

            def changes(self):
                return [{
                    "student_id": first.id,
                    "name": "Anna Maria",
                    "surnames": "Serra",
                    "group_name": "2A",
                }]

            def effective_date(self):
                return "2026-09-01"

        messages = []
        monkeypatch.setattr(
            QMessageBox, "information", lambda *args: messages.append(args[2])
        )
        controller.bulk_dialog_factory = AcceptedBulkDialog

        controller.bulk_edit()
        qtbot.waitUntil(lambda: not controller._bulk_edit.is_running(), timeout=5000)

        updated = services.students.get_by_id(first.id)
        assert updated.name == "Anna Maria"
        assert updated.group_name == "2A"
        assert "Alumnes actualitzats: 1" in messages[0]
        assert errors == []
    finally:
        database.close()
