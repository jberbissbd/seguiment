from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.application import create_services
from tutopy.controllers.report_controller import ReportController
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.services.exceptions import ValidationError
from tutopy.ui.main_window import MainWindow
from tutopy.database.database import Database


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "reports-controller.db")).connect()
    yield database
    database.close()


class AcceptedTermDialog:
    values_to_return = {}

    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def values(self):
        return dict(self.values_to_return)


class AcceptedExportDialog:
    order = []
    include = True
    format = "xlsx"

    def __init__(self, *args, **kwargs):
        self.include_terms = SimpleNamespace(isChecked=lambda: self.include)
        self.include_documents = SimpleNamespace(isChecked=lambda: False)

    def exec(self):
        return QDialog.DialogCode.Accepted

    def category_order(self):
        return list(self.order)

    def export_format(self):
        return self.format


class AcceptedBatchExportDialog(AcceptedExportDialog):
    ids = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_documents = SimpleNamespace(isChecked=lambda: False)

    def student_ids(self):
        return list(self.ids)


def _controller(db, qtbot, tmp_path, monkeypatch):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Bona evolució"
    ))
    course = services.academic_courses.get_by_course("2025-2026")
    window = MainWindow()
    qtbot.addWidget(window)
    errors = []
    controller = ReportController(
        window, services.students, services.academic_courses,
        services.report_configuration, services.report_files,
        services.student_exports,
        term_dialog=AcceptedTermDialog, export_dialog=AcceptedExportDialog,
        batch_export_dialog=AcceptedBatchExportDialog,
        error_handler=errors.append, confirm_delete=lambda _name: True,
    )
    destination = tmp_path / "informe.xlsx"
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: (str(destination), ""))
    return services, student, category, course, window, controller, destination, errors


def test_controlador_crea_edita_i_elimina_configuracio(db, qtbot, tmp_path, monkeypatch):
    services, _student, _category, course, window, controller, _path, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    values = {
        "academic_course_id": course.id,
        "group_name": "4t A",
        "second_term_start": "2026-01-08",
        "third_term_start": "2026-04-07",
    }
    monkeypatch.setattr(AcceptedTermDialog, "values_to_return", values)
    controller.create_term_configuration()
    configuration = services.report_configuration.get_term_configurations()[0]
    assert window.data_tools.term_table.rowCount() == 1
    values["third_term_start"] = "2026-04-10"
    controller.edit_term_configuration(configuration.id)
    assert services.report_configuration.get_term_configurations()[0].third_term_start == "2026-04-10"
    controller.delete_term_configuration(configuration.id)
    assert services.report_configuration.get_term_configurations() == []
    assert errors == []


def test_controlador_exporta_i_recorda_ordre(db, qtbot, tmp_path, monkeypatch):
    services, student, academic, _course, _window, controller, destination, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    family = services.categories.create(CategoryNew("Família"))
    monkeypatch.setattr(AcceptedExportDialog, "order", [family.id, academic.id])
    monkeypatch.setattr(AcceptedExportDialog, "include", False)
    controller.export_student(student.id)
    assert destination.is_file()
    assert [item.id for item in services.report_configuration.get_ordered_categories()] == [
        family.id, academic.id
    ]
    assert errors == []


def test_controlador_exporta_document_de_text(db, qtbot, tmp_path, monkeypatch):
    services, student, academic, _course, _window, controller, _destination, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    monkeypatch.setattr(AcceptedExportDialog, "order", [academic.id])
    monkeypatch.setattr(AcceptedExportDialog, "format", "docx")
    destination = tmp_path / "informe.docx"
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: (str(destination), ""))
    controller.export_student(student.id)
    assert destination.is_file()
    assert errors == []


@pytest.mark.parametrize("report_format", ["odt", "pdf"])
def test_controlador_exporta_formats_oberts(
    db, qtbot, tmp_path, monkeypatch, report_format
):
    services, student, academic, _course, _window, controller, _destination, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    monkeypatch.setattr(AcceptedExportDialog, "order", [academic.id])
    monkeypatch.setattr(AcceptedExportDialog, "format", report_format)
    destination = tmp_path / f"informe.{report_format}"
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: (str(destination), ""))

    controller.export_student(student.id)

    assert destination.is_file()
    assert errors == []


def test_controlador_configura_i_elimina_logotip_global(
    db, qtbot, tmp_path, monkeypatch
):
    services, _student, _academic, _course, window, controller, _destination, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    services.report_configuration.storage_dir = tmp_path / "reporting"
    logo = tmp_path / "logo.png"
    logo.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8"
        b"\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *args: (str(logo), ""))
    controller.configure_report_logo()
    assert services.report_configuration.get_header_image().is_file()
    assert window.data_tools.report_logo_remove_button.isEnabled()
    controller.remove_report_logo()
    assert services.report_configuration.get_header_image() is None
    assert not window.data_tools.report_logo_remove_button.isEnabled()
    assert errors == []


def test_controlador_respecta_cancel_lacions_i_ids_inexistents(
    db, qtbot, tmp_path, monkeypatch
):
    _services, student, _category, _course, _window, controller, _path, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )

    class RejectedDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return QDialog.DialogCode.Rejected

    controller.term_dialog = RejectedDialog
    controller.export_dialog = RejectedDialog
    controller.batch_export_dialog = RejectedDialog
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("", ""))

    controller.configure_report_logo()
    controller.create_term_configuration()
    controller.edit_term_configuration(999)
    controller.configure_category_order()
    controller.export_student(999)
    controller.export_student(student.id)
    controller.export_students()

    assert errors == [
        "No s’ha trobat la configuració de trimestres.",
        "No s’ha trobat l’alumne.",
    ]


def test_controlador_mostra_errors_de_configuracio_i_exportacio(
    db, qtbot, tmp_path, monkeypatch
):
    services, student, category, course, _window, controller, _path, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    values = {
        "academic_course_id": course.id,
        "group_name": "4t A",
        "second_term_start": "2026-01-08",
        "third_term_start": "2026-04-07",
    }
    monkeypatch.setattr(AcceptedTermDialog, "values_to_return", values)
    services.report_configuration.save_term_configuration = lambda _data: (
        (_ for _ in ()).throw(ValidationError("configuració incorrecta"))
    )
    controller.create_term_configuration()

    controller.confirm_delete = lambda _name: False
    controller.delete_term_configuration(1)

    controller.confirm_delete = lambda _name: True
    services.report_configuration.delete_term_configuration = lambda _id: (
        (_ for _ in ()).throw(ValidationError("no es pot eliminar"))
    )
    controller.delete_term_configuration(1)

    monkeypatch.setattr(AcceptedExportDialog, "order", [category.id])
    services.report_configuration.set_category_order = lambda _order: (
        (_ for _ in ()).throw(ValidationError("ordre incorrecte"))
    )
    controller.configure_category_order()
    controller.export_student(student.id)

    assert errors == [
        "configuració incorrecta", "no es pot eliminar", "ordre incorrecte",
        "ordre incorrecte",
    ]


def test_controlador_exporta_diversos_alumnes(db, qtbot, tmp_path, monkeypatch):
    services, student, academic, _course, _window, controller, _destination, errors = (
        _controller(db, qtbot, tmp_path, monkeypatch)
    )
    second = services.students.create(StudentNew("Pau", "Puig", "4t B"))
    services.notes.create(NoteNew(
        second.id, academic.id, "2026-02-02", 0, "Seguiment"
    ))
    monkeypatch.setattr(AcceptedBatchExportDialog, "ids", [student.id, second.id])
    monkeypatch.setattr(AcceptedBatchExportDialog, "order", [academic.id])
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(tmp_path / "lots"))
    messages = []
    monkeypatch.setattr(QMessageBox, "information",
                        lambda *args: messages.append(args[2]))

    controller.export_students()

    qtbot.waitUntil(lambda: bool(messages), timeout=5000)
    assert any("Alumnes exportats: 2" in message for message in messages)
    assert len(list((tmp_path / "lots").glob("Informes *"))) == 1
    assert errors == []
