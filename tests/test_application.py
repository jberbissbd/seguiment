import pytest

from tutopy.application import ServiceContainer, create_services
from tutopy.database.database import Database
from tutopy.services.note_service import NoteService
from tutopy.services.student_service import StudentService
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService


def test_create_services_requereix_database_connectada(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    with pytest.raises(RuntimeError, match="connectada"):
        create_services(database)


def test_create_services_compon_la_capa_de_negoci(tmp_path):
    database = Database(str(tmp_path / "test.db")).connect()
    try:
        services = create_services(database)
        assert isinstance(services, ServiceContainer)
        assert isinstance(services.students, StudentService)
        assert isinstance(services.notes, NoteService)
        assert isinstance(services.report_configuration, ReportConfigurationService)
        assert isinstance(services.spreadsheet_reports, SpreadsheetReportService)
        assert not hasattr(services, "database")
    finally:
        database.close()


def test_main_es_importable_sense_executar_la_ui():
    from tutopy.main import main

    assert callable(main)
