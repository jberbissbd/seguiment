from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.controllers.data_management_controller import DataManagementController
from tutopy.models.bulk_import import ClearDataResult, ImportIssue, ImportResult
from tutopy.services.exceptions import ValidationError
from tutopy.ui.main_window import MainWindow


class ImporterStub:
    def __init__(self):
        self.preview = SimpleNamespace(issues=(), conflicts=())
        self.result = ImportResult(1, 2, 3, 4, 5)
        self.created_at = None
        self.executed = None
        self.error = None

    def create_template(self, filename):
        if self.error:
            raise self.error
        self.created_at = filename
        return filename

    def analyze(self, filename):
        if self.error:
            raise self.error
        return self.preview

    def execute(self, preview, decisions=()):
        self.executed = (preview, decisions)
        return self.result


class DataServiceStub:
    def __init__(self, result=ClearDataResult()):
        self.result = result
        self.called = False
        self.error = None

    def delete_all(self):
        self.called = True
        if self.error:
            raise self.error
        return self.result


@pytest.fixture
def controller_env(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window.errors = []
    window.issues = []
    window.show_error = window.errors.append
    window.show_import_issues = window.issues.append
    importer = ImporterStub()
    data = DataServiceStub()
    changed = []
    controller = DataManagementController(window, importer, data,
                                          on_changed=lambda: changed.append(True))
    messages = []
    monkeypatch.setattr(QMessageBox, "information",
                        lambda *args: messages.append(args[2]))
    return window, importer, data, controller, changed, messages


def test_exporta_plantilla_i_admet_cancel_lacio(controller_env, monkeypatch):
    window, importer, _, controller, _, _ = controller_env
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    controller.export_template()
    assert importer.created_at is None
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: ("/tmp/plantilla.xlsx", ""))
    controller.export_template()
    assert importer.created_at == "/tmp/plantilla.xlsx"
    assert "Plantilla desada" in window.statusBar().currentMessage()


def test_exportacio_mostra_error_de_domini(controller_env, monkeypatch):
    window, importer, _, controller, _, _ = controller_env
    importer.error = ValidationError("no es pot desar")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("fitxer.xlsx", ""))
    controller.export_template()
    assert window.errors == ["no es pot desar"]


def test_importacio_cancel_lada_o_amb_incidencies_no_executa(controller_env, monkeypatch):
    window, importer, _, controller, _, _ = controller_env
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("", ""))
    controller.import_spreadsheet()
    assert importer.executed is None
    issue = ImportIssue("Alumnes", 3, "falta el nom")
    importer.preview = SimpleNamespace(issues=(issue,), conflicts=())
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert window.issues == [(issue,)]
    assert importer.executed is None


def test_importacio_sense_conflictes_refresca_i_resumeix(controller_env, monkeypatch):
    _, importer, _, controller, changed, messages = controller_env
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert importer.executed == (importer.preview, ())
    assert changed == [True]
    assert "Alumnes creats: 1" in messages[0]
    assert "Categories reutilitzades: 5" in messages[0]


def test_importacio_amb_conflictes_aplica_decisions(controller_env, monkeypatch):
    _, importer, _, controller, changed, _ = controller_env
    importer.preview = SimpleNamespace(issues=(), conflicts=(object(),))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))

    class AcceptedDialog:
        def __init__(self, *args): pass
        def exec(self): return QDialog.DialogCode.Accepted
        def decisions(self): return ("decisió",)

    controller.conflict_dialog = AcceptedDialog
    controller.import_spreadsheet()
    assert importer.executed == (importer.preview, ("decisió",))
    assert changed == [True]


def test_importacio_amb_conflictes_es_pot_cancel_lar(controller_env, monkeypatch):
    _, importer, _, controller, changed, _ = controller_env
    importer.preview = SimpleNamespace(issues=(), conflicts=(object(),))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))

    class RejectedDialog:
        def __init__(self, *args): pass
        def exec(self): return QDialog.DialogCode.Rejected

    controller.conflict_dialog = RejectedDialog
    controller.import_spreadsheet()
    assert importer.executed is None
    assert changed == []


def test_importacio_mostra_errors(controller_env, monkeypatch):
    window, importer, _, controller, _, _ = controller_env
    importer.error = ValidationError("full incorrecte")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert window.errors == ["full incorrecte"]


def test_esborrat_cancel_lacio_error_i_exit(controller_env, monkeypatch):
    window, _, data, controller, changed, messages = controller_env

    class Dialog:
        result = QDialog.DialogCode.Rejected
        def __init__(self, *args): pass
        def exec(self): return self.result

    controller.clear_dialog = Dialog
    controller.clear_all()
    assert not data.called
    monkeypatch.setattr(Dialog, "result", QDialog.DialogCode.Accepted)
    data.error = ValidationError("no s’ha pogut eliminar")
    controller.clear_all()
    assert window.errors == ["no s’ha pogut eliminar"]
    data.error = None
    data.result = ClearDataResult(2, ("fitxer.pdf: permís denegat",))
    controller.clear_all()
    assert changed == [True]
    assert "S’han eliminat totes les dades" in messages[0]
    assert "fitxer.pdf: permís denegat" in messages[0]
