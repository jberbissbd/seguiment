"""Escenaris compartits per provar controladors sense diàlegs bloquejants."""

from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.application import create_services
from tutopy.controllers.data_management_controller import DataManagementController
from tutopy.controllers.report_controller import ReportController
from tutopy.controllers.student_controller import StudentController
from tutopy.database.database import Database
from tutopy.models.bulk_import import ClearDataResult, ImportResult
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.ui.main_window import MainWindow


@pytest.fixture
def controller_app(qtbot, tmp_path, monkeypatch):
    """Aïlla serveis reals i captura els missatges de la finestra principal."""
    database = Database(str(tmp_path / "controllers.db")).connect()
    try:
        services = create_services(database)
        services.documents.storage_dir = tmp_path / "documents"
        services.report_configuration.storage_dir = tmp_path / "reporting"
        window = MainWindow()
        qtbot.addWidget(window)
        errors, messages = [], []
        monkeypatch.setattr(window, "show_error", errors.append)
        monkeypatch.setattr(QMessageBox, "information", lambda *args: messages.append(args[2]))
        yield SimpleNamespace(services=services, window=window, errors=errors, messages=messages)
    finally:
        database.close()


@pytest.fixture
def student_env(controller_app):
    """Prepara un controlador amb un alumne seleccionat per comprovar canvis i errors."""
    env = controller_app
    env.student = env.services.students.create(StudentNew("Laia", "Serra", "4A"))
    env.controller = StudentController(
        env.window,
        env.services.students,
        confirm_delete=lambda _name: True,
    )
    env.controller.start()
    env.window.student_list.select_student(env.student.id)
    return env


@pytest.fixture
def report_env(controller_app, tmp_path, monkeypatch):
    """Prepara un informe real i un formulari configurable sense interacció modal."""
    env = controller_app
    env.student = env.services.students.create(StudentNew("Laia", "Serra", "4A"))
    env.category = env.services.categories.create(CategoryNew("Seguiment"))
    env.services.notes.create(
        NoteNew(
            env.student.id,
            env.category.id,
            "2026-02-01",
            0,
            "Bona evolució",
        )
    )
    env.options = SimpleNamespace(documents=False, format="xlsx", ids=[env.student.id])
    form = SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        export_format=lambda: env.options.format,
        category_order=lambda: [env.category.id],
        student_ids=lambda: env.options.ids,
        include_terms=SimpleNamespace(isChecked=lambda: False),
        include_documents=SimpleNamespace(isChecked=lambda: env.options.documents),
    )
    env.controller = ReportController(
        env.window,
        env.services.students,
        env.services.academic_courses,
        env.services.report_configuration,
        env.services.report_files,
        env.services.student_exports,
        export_dialog=lambda *args, **kwargs: form,
        batch_export_dialog=lambda *args, **kwargs: form,
    )
    env.destination = tmp_path / "exportats"
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: str(env.destination))
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(env.destination / "informe.xlsx"), ""),
    )
    return env


class ImporterStub:
    """Simula una importació i permet injectar incidències i errors."""

    def __init__(self):
        """Inicialitza un resultat de prova sense cap operació executada."""
        self.preview = SimpleNamespace(issues=(), conflicts=())
        self.result = ImportResult(1, 2, 3, 4, 5)
        self.created_at = None
        self.executed = None
        self.error = None

    def create_template(self, filename):
        """Registra la destinació o propaga l’error configurat."""
        if self.error:
            raise self.error
        self.created_at = filename
        return filename

    def analyze(self, filename):
        """Retorna la previsualització o l’error configurat."""
        if self.error:
            raise self.error
        return self.preview

    def execute(self, preview, decisions=()):
        """Registra les decisions rebudes i retorna el resultat de prova."""
        self.executed = (preview, decisions)
        return self.result


class DataServiceStub:
    """Simula l’esborrat de dades sense modificar una base de dades."""

    def __init__(self, result=None):
        """Prepara el resultat o error que retornarà l’esborrat."""
        self.result = ClearDataResult() if result is None else result
        self.called = False
        self.error = None

    def delete_all(self):
        """Registra la petició i retorna el resultat o propaga l’error."""
        self.called = True
        if self.error:
            raise self.error
        return self.result


@pytest.fixture
def data_management_env(qtbot, monkeypatch):
    """Captura errors, avisos i refrescos del controlador de gestió de dades."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.errors = []
    window.issues = []
    window.show_error = window.errors.append
    window.show_import_issues = window.issues.append
    importer = ImporterStub()
    data = DataServiceStub()
    changed = []
    controller = DataManagementController(
        window, importer, data, on_changed=lambda: changed.append(True)
    )
    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args: messages.append(args[2]))
    return window, importer, data, controller, changed, messages
