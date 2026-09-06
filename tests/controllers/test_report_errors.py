"""Garanties d'exportació, cancel·lació i errors dels informes."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog

from tutopy.models.messaging import StudentNew
from tutopy.models.reporting import TermConfigurationNew
from tutopy.services.exceptions import ValidationError


def test_exportacio_individual_inclou_documents_reals(report_env, tmp_path):
    """L'informe i els adjunts es copien junts conservant-ne el contingut."""
    env = report_env
    source = tmp_path / "acta.txt"
    source.write_text("Acta de reunió", encoding="utf-8")
    env.services.documents.import_file(
        env.student.id,
        "Acta",
        "Reunió",
        str(source),
        "2026-02-01",
    )
    env.options.documents = True
    env.controller.export_student(env.student.id)
    assert len(list(env.destination.rglob("informe.xlsx"))) == 1
    documents = list(env.destination.rglob("*.txt"))
    assert len(documents) == 1
    assert documents[0].read_text() == "Acta de reunió"
    assert env.errors == []
    assert "Informe i documents desats" in env.window.statusBar().currentMessage()


@pytest.mark.parametrize("documents", [False, True], ids=["informe", "amb-adjunts"])
def test_cancel_lar_destinacio_no_escriu_ni_canvia_configuracio(
    report_env,
    monkeypatch,
    documents,
):
    """Cancel·lar la destinació no modifica l'ordre de categories ni genera fitxers."""
    env = report_env
    env.options.documents = documents
    store = Mock(wraps=env.services.report_configuration.set_category_order)
    monkeypatch.setattr(env.services.report_configuration, "set_category_order", store)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: "")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    env.controller.export_student(env.student.id)
    store.assert_not_called()
    assert not env.destination.exists()
    assert env.errors == []


@pytest.mark.parametrize("error", [ValidationError("document absent"), OSError("disc ple")])
def test_error_exportant_adjunts_no_anuncia_exit(report_env, monkeypatch, error):
    """Un error durant l'exportació individual es mostra sense confirmar-ne l'èxit."""
    env = report_env
    env.options.documents = True
    monkeypatch.setattr(env.services.student_exports, "export_student", Mock(side_effect=error))
    env.controller.export_student(env.student.id)
    assert env.errors == [str(error)]
    assert "desats" not in env.window.statusBar().currentMessage()


def test_format_desconegut_no_obre_selector_de_fitxer(report_env, monkeypatch):
    """La validació del format atura l'exportació abans de demanar una destinació."""
    env = report_env
    env.options.format = "desconegut"
    selector = Mock()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", selector)
    env.controller.export_student(env.student.id)
    selector.assert_not_called()
    assert len(env.errors) == 1
    assert "format" in env.errors[0]


@pytest.mark.parametrize(
    "operation, method",
    [
        ("configure_report_logo", "set_header_image"),
        ("remove_report_logo", "clear_header_image"),
    ],
)
def test_errors_de_logotip_es_comuniquen(report_env, monkeypatch, operation, method):
    """Una configuració de logotip fallida no es presenta com a aplicada."""
    env = report_env
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: ("logo.png", ""))
    monkeypatch.setattr(
        env.services.report_configuration,
        method,
        Mock(side_effect=ValidationError("logotip invàlid")),
    )
    getattr(env.controller, operation)()
    assert env.errors == ["logotip invàlid"]
    assert "Logotip" not in env.window.statusBar().currentMessage()


def test_configuracio_de_grup_antic_es_pot_obrir(report_env, monkeypatch):
    """L'edició conserva un grup històric encara que ja no hi hagi alumnes assignats."""
    env = report_env
    course = env.services.academic_courses.get_by_course("2025-2026")
    configuration = env.services.report_configuration.save_term_configuration(
        TermConfigurationNew(
            course.id,
            "Grup antic",
            "2026-01-08",
            "2026-04-07",
        )
    )
    received = []

    def dialog(courses, groups, original, **kwargs):
        received.append((groups, original))
        return SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected)

    monkeypatch.setattr(env.controller, "term_dialog", dialog)
    env.controller.edit_term_configuration(configuration.id)
    assert received == [(["4A", "Grup antic"], configuration)]
    assert (
        env.services.report_configuration.get_term_configuration_by_id(configuration.id)
        == configuration
    )


def test_ordre_categories_acceptat_es_desa(report_env):
    """Acceptar la configuració desa l'ordre seleccionat i ho confirma."""
    env = report_env
    env.controller.configure_category_order()
    assert env.services.report_configuration.get_ordered_categories() == [env.category]
    assert "Ordre de categories desat" in env.window.statusBar().currentMessage()


@pytest.mark.parametrize("reason", ["busy", "destination", "preparation"])
def test_exportacio_massiva_no_inicia_tasca_si_no_esta_preparada(
    report_env,
    monkeypatch,
    reason,
):
    """Les peticions duplicades, cancel·lades o invàlides no inicien un treballador."""
    env = report_env
    start = Mock()
    monkeypatch.setattr(env.controller._batch_export, "start", start)
    if reason == "busy":
        monkeypatch.setattr(env.controller._batch_export, "is_running", lambda: True)
    elif reason == "destination":
        monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: "")
    else:
        monkeypatch.setattr(
            env.services.student_exports,
            "prepare_students_export",
            Mock(side_effect=ValidationError("selecció invàlida")),
        )
    env.controller.export_students()
    start.assert_not_called()
    assert env.errors == (["selecció invàlida"] if reason == "preparation" else [])
    assert not env.destination.exists()


def test_error_del_treballador_tanca_exportacio(report_env, monkeypatch, qtbot):
    """Un error asíncron tanca el progrés i no mostra el resum d'èxit."""
    env = report_env
    monkeypatch.setattr(
        env.services.student_exports,
        "export_prepared",
        Mock(side_effect=OSError("disc ple")),
    )
    env.controller.export_students()
    qtbot.waitUntil(lambda: bool(env.errors), timeout=5000)
    assert env.errors == ["disc ple"]
    assert env.messages == []
    assert not env.controller._batch_export.is_running()
    assert env.controller._batch_export.progress is None


@pytest.mark.parametrize("cancelled", [False, True])
def test_resum_massiu_distingeix_errors_i_cancel_lacio(report_env, monkeypatch, qtbot, cancelled):
    """El resum mostra alumnes fallits o cancel·lació amb el nombre real d'exportats."""
    env = report_env
    if cancelled:
        monkeypatch.setattr(
            env.services.student_exports,
            "export_prepared",
            Mock(
                return_value=SimpleNamespace(
                    exported=0,
                    cancelled=True,
                    failures=(),
                    destination=str(env.destination),
                )
            ),
        )
    else:
        empty = env.services.students.create(StudentNew("Pau", "Puig", "4B"))
        env.options.ids = [empty.id, env.student.id]
    env.controller.export_students()
    qtbot.waitUntil(lambda: bool(env.messages), timeout=5000)
    if cancelled:
        assert "Exportació cancel·lada" in env.messages[0]
        assert "Alumnes exportats: 0" in env.messages[0]
    else:
        assert "Errors: 1" in env.messages[0]
        assert "Puig, Pau" in env.messages[0]
        assert "Alumnes exportats: 1" in env.messages[0]
    assert env.errors == []
