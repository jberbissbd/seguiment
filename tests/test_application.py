import pytest
from types import SimpleNamespace

from tutopy.application import ServiceContainer, create_services
from tutopy.database.database import Database
from tutopy.services.note_service import NoteService
from tutopy.services.student_service import StudentService
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService
from tutopy.services.word_report_service import WordReportService
from tutopy.services.student_export_service import StudentExportService
from tutopy.services.statistics_service import StatisticsService
from tutopy.main import ControllerContainer, create_controllers
from tutopy.ui.main_window import MainWindow


def test_create_services_requereix_database_connectada(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    with pytest.raises(RuntimeError, match="connectada"):
        create_services(database)


@pytest.mark.integration
def test_create_services_compon_la_capa_de_negoci(tmp_path):
    database = Database(str(tmp_path / "test.db")).connect()
    try:
        services = create_services(database)
        assert isinstance(services, ServiceContainer)
        assert isinstance(services.students, StudentService)
        assert isinstance(services.notes, NoteService)
        assert isinstance(services.report_configuration, ReportConfigurationService)
        assert isinstance(services.spreadsheet_reports, SpreadsheetReportService)
        assert isinstance(services.word_reports, WordReportService)
        assert isinstance(services.student_exports, StudentExportService)
        assert isinstance(services.statistics, StatisticsService)
        assert not hasattr(services, "database")
    finally:
        database.close()


def test_main_es_importable_sense_executar_la_ui():
    from tutopy.main import main

    assert callable(main)


def test_controller_container_inicia_nomes_controladors_visibles():
    calls = []

    def controller(name):
        return SimpleNamespace(start=lambda: calls.append(name))

    container = ControllerContainer(
        main=controller("main"), students=controller("students"),
        notes=controller("notes"), categories=controller("categories"),
        student_related=controller("related"),
        data_management=controller("data"), reports=controller("reports"),
        statistics=controller("statistics"),
    )

    container.start()

    assert calls == [
        "main", "students", "notes", "categories", "reports", "statistics",
    ]


@pytest.mark.ui
def test_create_controllers_compon_i_inicia_la_ui(tmp_path, qtbot):
    database = Database(str(tmp_path / "controllers.db")).connect()
    try:
        services = create_services(database)
        window = MainWindow()
        qtbot.addWidget(window)

        controllers = create_controllers(window, services)
        controllers.start()

        assert isinstance(controllers, ControllerContainer)
        assert controllers.students.service is services.students
        assert controllers.notes.note_service is services.notes
        assert window.student_list.list_widget.count() == 0
    finally:
        database.close()


def test_main_configura_cicle_de_vida_sense_executar_qt(monkeypatch):
    import tutopy.main as main_module

    events = []

    class Signal:
        def connect(self, callback):
            events.append(("close-connected", callback))

    class FakeApplication:
        def __init__(self, arguments):
            events.append(("application", arguments))
            self.aboutToQuit = Signal()

        def setApplicationName(self, name):
            events.append(("name", name))

        def setWindowIcon(self, icon):
            events.append(("icon", icon))

        def exec(self):
            return 17

    database = SimpleNamespace(close=lambda: None)
    database_factory = SimpleNamespace(
        connect=lambda: database,
    )
    window = SimpleNamespace(show=lambda: events.append(("show", True)))
    controllers = SimpleNamespace(start=lambda: events.append(("start", True)))

    monkeypatch.setattr(main_module.QGuiApplication,
                        "setHighDpiScaleFactorRoundingPolicy", lambda *_: None)
    monkeypatch.setattr(main_module, "QApplication", FakeApplication)
    monkeypatch.setattr(main_module, "application_icon", lambda: "icon")
    monkeypatch.setattr(main_module, "get_db_path", lambda: "test.db")
    monkeypatch.setattr(main_module, "Database", lambda _path: database_factory)
    monkeypatch.setattr(main_module, "create_services", lambda _db: "services")
    monkeypatch.setattr(main_module, "MainWindow", lambda: window)
    monkeypatch.setattr(
        main_module, "create_controllers", lambda _window, _services: controllers
    )

    assert main_module.main() == 17
    assert window.controllers is controllers
    assert ("name", "Tutopy") in events
    assert ("start", True) in events
    assert ("show", True) in events
