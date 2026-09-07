from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog

from tutopy.models.bulk_import import ClearDataResult, ImportIssue
from tutopy.services.exceptions import ValidationError


@pytest.mark.parametrize("action", ["export_all_students", "import_transfer"])
def test_transferencia_sense_servei_no_obre_dialegs(data_management_env, monkeypatch, action):
    """L'absència del servei s'informa abans de demanar cap fitxer."""
    window, _, _, controller, changed, messages = data_management_env
    controller.student_service = SimpleNamespace(get_all=lambda: [SimpleNamespace(id=1)])

    def unexpected(*args):
        pytest.fail("No s'ha d'obrir un selector sense servei de transferència")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", unexpected)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", unexpected)
    getattr(controller, action)()
    assert window.errors == ["El servei de transferència no està disponible."]
    assert changed == messages == []


@pytest.mark.parametrize("action, presenter", [
    ("export_all_students", "_transfer_export"), ("import_transfer", "_transfer_analysis"),
])
def test_transferencia_en_curs_no_inicia_una_segona(
    data_management_env, monkeypatch, action, presenter,
):
    """Una segona petició conserva la tasca que ja està activa."""
    window, _, _, controller, _, _ = data_management_env
    controller.transfer_service = Mock()
    controller.student_service = SimpleNamespace(get_all=lambda: [SimpleNamespace(id=1)])
    monkeypatch.setattr(getattr(controller, presenter), "is_running", lambda: True)
    getattr(controller, action)()
    assert controller.transfer_service.mock_calls == []
    assert window.statusBar().currentMessage()
    assert window.errors == []


@pytest.mark.parametrize("responses, expected_error", [
    ([("", False)], None),
    ([("contrasenya", True), ("", False)], None),
    ([("curta", True), ("curta", True)], "com a mínim 8"),
])
def test_contrasenya_cancel_lada_o_curta_no_prepara_exportacio(
    data_management_env, monkeypatch, responses, expected_error,
):
    """L'exportació no accedeix a dades fins que la contrasenya és vàlida."""
    window, _, _, controller, _, _ = data_management_env
    controller.transfer_service = Mock()
    controller.student_service = SimpleNamespace(get_all=lambda: [SimpleNamespace(id=1)])
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("paquet.tpy", ""))
    answers = iter(responses)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: next(answers))
    controller.export_all_students()
    controller.transfer_service.prepare_export.assert_not_called()
    if expected_error:
        assert expected_error in window.errors[0]
    else:
        assert window.errors == []


@pytest.mark.parametrize("stage", ["export", "analysis", "execution"])
@pytest.mark.parametrize("error", [
    ValidationError("paquet invàlid"), RuntimeError("detall intern reservat"),
])
def test_errors_del_treballador_no_anuncien_exit(
    data_management_env, monkeypatch, qtbot, stage, error, caplog,
):
    """Una fallada asíncrona tanca el progrés i no refresca dades com si hi hagués èxit."""
    window, _, _, controller, changed, messages = data_management_env
    transfer = Mock()
    transfer.prepare_export.return_value = "preparació"
    transfer.prepare_analysis.return_value = "anàlisi"
    transfer.complete_analysis.return_value = SimpleNamespace(conflicts=(), student_count=1)
    method = {"export": "export_prepared", "analysis": "prepare_analysis",
              "execution": "execute_with_worker_connection"}[stage]
    getattr(transfer, method).side_effect = error
    controller.transfer_service = transfer
    controller.student_service = SimpleNamespace(get_all=lambda: [SimpleNamespace(id=1)])
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("paquet.tpy", ""))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("paquet.tpy", ""))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: ("contrasenya", True))
    if stage == "export":
        controller.export_all_students()
    else:
        controller.import_transfer()
    qtbot.waitUntil(lambda: bool(window.errors), timeout=5000)
    presenter = getattr(controller, {
        "export": "_transfer_export", "analysis": "_transfer_analysis",
        "execution": "_transfer_execution",
    }[stage])
    assert not presenter.is_running()
    assert presenter.progress is None
    assert changed == messages == []
    if isinstance(error, ValidationError):
        assert window.errors == ["paquet invàlid"]
    else:
        assert "RuntimeError" in window.errors[0]
        assert "detall intern reservat" not in window.errors[0]
        assert "Error inesperat" in caplog.text


@pytest.mark.parametrize("accepted", [False, True])
def test_conflictes_transferencia_respecten_la_decisio(
    data_management_env, monkeypatch, qtbot, accepted,
):
    """Cancel·lar conflictes atura la importació; acceptar transmet les decisions."""
    window, _, _, controller, changed, messages = data_management_env
    preview = SimpleNamespace(conflicts=("conflicte",), student_count=1)
    transfer = Mock()
    transfer.complete_analysis.return_value = preview
    transfer.execute_with_worker_connection.return_value = SimpleNamespace(cancelled=True)
    controller.transfer_service = transfer
    controller.transfer_conflict_dialog = lambda *args: SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted if accepted else QDialog.DialogCode.Rejected,
        decisions=lambda: ("conservar",),
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("paquet.tpy", ""))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: ("contrasenya", True))
    controller.import_transfer()
    qtbot.waitUntil(
        lambda: transfer.complete_analysis.called and not controller._transfer_execution.is_running(),
        timeout=5000,
    )
    if accepted:
        args, kwargs = transfer.execute_with_worker_connection.call_args
        assert args == (preview, ("conservar",))
        assert kwargs["password"] == "contrasenya"
        assert "cancel·lada" in window.statusBar().currentMessage()
    else:
        transfer.execute_with_worker_connection.assert_not_called()
    assert window.errors == changed == messages == []


def test_exporta_plantilla_i_admet_cancel_lacio(data_management_env, monkeypatch):
    window, importer, _, controller, _, _ = data_management_env
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    controller.export_template()
    assert importer.created_at is None
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: ("/tmp/plantilla.xlsx", ""))
    controller.export_template()
    assert importer.created_at == "/tmp/plantilla.xlsx"
    assert "Plantilla desada" in window.statusBar().currentMessage()


def test_exportacio_mostra_error_de_domini(data_management_env, monkeypatch):
    window, importer, _, controller, _, _ = data_management_env
    importer.error = ValidationError("no es pot desar")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("fitxer.xlsx", ""))
    controller.export_template()
    assert window.errors == ["no es pot desar"]


def test_importacio_cancel_lada_o_amb_incidencies_no_executa(data_management_env, monkeypatch):
    window, importer, _, controller, _, _ = data_management_env
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("", ""))
    controller.import_spreadsheet()
    assert importer.executed is None
    issue = ImportIssue("Alumnes", 3, "falta el nom")
    importer.preview = SimpleNamespace(issues=(issue,), conflicts=())
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert window.issues == [(issue,)]
    assert importer.executed is None


def test_importacio_sense_conflictes_refresca_i_resumeix(data_management_env, monkeypatch):
    _, importer, _, controller, changed, messages = data_management_env
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert importer.executed == (importer.preview, ())
    assert changed == [True]
    assert "Alumnes creats: 1" in messages[0]
    assert "Categories reutilitzades: 5" in messages[0]


def test_importacio_amb_conflictes_aplica_decisions(data_management_env, monkeypatch):
    _, importer, _, controller, changed, _ = data_management_env
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


def test_importacio_amb_conflictes_es_pot_cancel_lar(data_management_env, monkeypatch):
    _, importer, _, controller, changed, _ = data_management_env
    importer.preview = SimpleNamespace(issues=(), conflicts=(object(),))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))

    class RejectedDialog:
        def __init__(self, *args): pass
        def exec(self): return QDialog.DialogCode.Rejected

    controller.conflict_dialog = RejectedDialog
    controller.import_spreadsheet()
    assert importer.executed is None
    assert changed == []


def test_importacio_mostra_errors(data_management_env, monkeypatch):
    window, importer, _, controller, _, _ = data_management_env
    importer.error = ValidationError("full incorrecte")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("dades.xlsx", ""))
    controller.import_spreadsheet()
    assert window.errors == ["full incorrecte"]


def test_esborrat_cancel_lacio_error_i_exit(data_management_env, monkeypatch):
    window, _, data, controller, changed, messages = data_management_env

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


def test_transferencia_exporta_i_importa_paquets(
    data_management_env, monkeypatch, tmp_path, qtbot
):
    window, _, _, controller, changed, messages = data_management_env

    class TransferStub:
        def __init__(self):
            self.exported = None
            self.executed = None

        def prepare_export(self, student_ids, filename, password):
            self.exported = (student_ids, filename, password)
            return filename

        def export_prepared(
            self, preparation, progress_callback=None, cancel_requested=None
        ):
            progress_callback(1, 1)
            return preparation

        def prepare_analysis(self, filename, password):
            return SimpleNamespace(source=filename, password=password)

        def complete_analysis(self, preparation):
            return SimpleNamespace(
                source=preparation.source, conflicts=(), student_count=1
            )

        def execute_with_worker_connection(
            self, preview, decisions=(), password="", progress_callback=None,
            cancel_requested=None,
        ):
            self.executed = (preview, decisions, password)
            progress_callback(1, 1)
            return SimpleNamespace(
                created=2, replaced=0, skipped=0,
                imported_as_new=0, documents=1, cancelled=False,
            )

    transfer = TransferStub()
    controller.transfer_service = transfer
    controller.student_service = SimpleNamespace(
        get_all=lambda: (SimpleNamespace(id=7),)
    )
    destination = str(tmp_path / "tots.tpy")
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *args: (destination, "")
    )
    passwords = iter((("contrasenya", True), ("contrasenya", True)))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: next(passwords))
    controller.export_all_students()
    qtbot.waitUntil(
        lambda: not controller._transfer_export.is_running(), timeout=5000
    )
    assert transfer.exported == ([7], destination, "contrasenya")

    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", lambda *args: (destination, "")
    )
    monkeypatch.setattr(
        QInputDialog, "getText", lambda *args: ("contrasenya", True)
    )
    controller.import_transfer()
    qtbot.waitUntil(lambda: bool(messages), timeout=5000)
    assert transfer.executed[1:] == ((), "contrasenya")
    assert changed == [True]
    assert "Alumnes creats: 2" in messages[0]


def test_transferencia_individual_exigeix_seleccio(data_management_env):
    window, _, _, controller, _, _ = data_management_env
    controller.transfer_service = object()

    controller.export_selected_student()

    assert window.errors == ["No hi ha alumnes disponibles per exportar."]


def test_transferencia_exporta_els_alumnes_marcats_del_mateix_widget(
    data_management_env, monkeypatch, tmp_path, qtbot
):
    window, _, _, controller, _, _ = data_management_env

    class TransferStub:
        exported = None

        def prepare_export(self, student_ids, filename, password):
            self.exported = (student_ids, filename, password)
            return filename

        def export_prepared(
            self, preparation, progress_callback=None, cancel_requested=None
        ):
            progress_callback(1, 1)
            return preparation

    transfer = TransferStub()
    controller.transfer_service = transfer
    students = (
        SimpleNamespace(id=11, full_name="Anna Serra", group_name="3r A"),
        SimpleNamespace(id=22, full_name="Biel Puig", group_name="3r B"),
    )
    controller.student_service = SimpleNamespace(get_all=lambda: students)

    class AcceptedDialog:
        def __init__(self, received, parent):
            assert received == students

        def exec(self):
            return QDialog.DialogCode.Accepted

        def student_ids(self):
            return [22]

    controller.transfer_selection_dialog = AcceptedDialog
    destination = str(tmp_path / "seleccio.tpy")
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *args: (destination, "")
    )
    passwords = iter((("contrasenya", True), ("contrasenya", True)))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: next(passwords))

    controller.export_selected_student()

    qtbot.waitUntil(
        lambda: not controller._transfer_export.is_running(), timeout=5000
    )
    assert transfer.exported == ([22], destination, "contrasenya")


def test_transferencia_valida_confirmacio_i_mostra_motiu_error(
    data_management_env, monkeypatch, tmp_path
):
    window, _, _, controller, _, _ = data_management_env

    class TransferStub:
        def prepare_export(self, student_ids, filename, password):
            raise OSError(13, "Permís denegat")

    controller.transfer_service = TransferStub()
    controller.student_service = SimpleNamespace(
        get_all=lambda: (SimpleNamespace(id=1),)
    )
    destination = str(tmp_path / "tots.tpy")
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *args: (destination, "")
    )
    passwords = iter((("contrasenya", True), ("diferent", True)))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: next(passwords))
    controller.export_all_students()
    assert window.errors == ["Les contrasenyes no coincideixen."]

    window.errors.clear()
    passwords = iter((("contrasenya", True), ("contrasenya", True)))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: next(passwords))
    controller.export_all_students()
    assert "Permís denegat" in window.errors[0]
