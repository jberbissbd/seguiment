from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog

from tutopy.application import create_services
from tutopy.controllers.report_controller import ReportController
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
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

    def __init__(self, *args, **kwargs):
        self.include_terms = SimpleNamespace(isChecked=lambda: self.include)

    def exec(self):
        return QDialog.DialogCode.Accepted

    def category_order(self):
        return list(self.order)


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
        services.report_configuration, services.spreadsheet_reports,
        term_dialog=AcceptedTermDialog, export_dialog=AcceptedExportDialog,
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
    AcceptedTermDialog.values_to_return = {
        "academic_course_id": course.id,
        "group_name": "4t A",
        "second_term_start": "2026-01-08",
        "third_term_start": "2026-04-07",
    }
    controller.create_term_configuration()
    configuration = services.report_configuration.get_term_configurations()[0]
    assert window.data_tools.term_table.rowCount() == 1
    AcceptedTermDialog.values_to_return["third_term_start"] = "2026-04-10"
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
    AcceptedExportDialog.order = [family.id, academic.id]
    AcceptedExportDialog.include = False
    controller.export_student(student.id)
    assert destination.is_file()
    assert [item.id for item in services.report_configuration.get_ordered_categories()] == [
        family.id, academic.id
    ]
    assert errors == []
