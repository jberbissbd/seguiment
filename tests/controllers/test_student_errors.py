"""Garanties de cancel·lació i errors del CRUD i l'edició massiva d'alumnes."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDialog

from tutopy.services.exceptions import ValidationError


@pytest.mark.parametrize("operation", ["create", "edit"])
def test_cancel_lar_formulari_conserva_alumnes_i_seleccio(student_env, monkeypatch, operation):
    """Cancel·lar no modifica la persistència ni perd l'alumne seleccionat."""
    env = student_env
    form = SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected)
    monkeypatch.setattr(env.controller, "dialog_factory", lambda **kwargs: form)
    getattr(env.controller, operation)(*([env.student.id] if operation == "edit" else []))
    assert env.services.students.get_all() == [env.student]
    assert env.window.student_list.current_student_id() == env.student.id
    assert env.errors == []


@pytest.mark.parametrize("operation", ["edit", "delete"])
def test_alumne_inexistent_no_obre_dialeg(student_env, monkeypatch, operation):
    """Una petició sobre un ID que ja no existeix no inicia cap modificació."""
    env = student_env
    dialog = Mock()
    confirm = Mock()
    monkeypatch.setattr(env.controller, "dialog_factory", dialog)
    monkeypatch.setattr(env.controller, "confirm_delete", confirm)
    getattr(env.controller, operation)(99999)
    dialog.assert_not_called()
    confirm.assert_not_called()
    assert env.services.students.get_all() == [env.student]
    assert env.errors == []


@pytest.mark.parametrize("operation", ["create", "edit", "delete"])
def test_error_de_domini_conserva_dades_i_detall(student_env, monkeypatch, operation):
    """Els errors de validació o d'eliminació no publiquen un èxit ni buiden el detall."""
    env = student_env
    form = SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        values=lambda: {"name": " ", "surnames": "Serra", "group_name": "4A"},
    )
    monkeypatch.setattr(env.controller, "dialog_factory", lambda **kwargs: form)
    if operation == "delete":
        monkeypatch.setattr(
            env.services.students,
            "delete",
            Mock(side_effect=ValidationError("no es pot eliminar")),
        )
    getattr(env.controller, operation)(*([] if operation == "create" else [env.student.id]))
    assert len(env.errors) == 1
    assert env.services.students.get_all() == [env.student]
    assert env.window.student_detail.current_student_id == env.student.id
    assert "correctament" not in env.window.statusBar().currentMessage()


@pytest.mark.parametrize("reason", ["busy", "empty", "cancelled"])
def test_edicio_massiva_no_inicia_operacions_sense_confirmacio(
    student_env,
    monkeypatch,
    reason,
):
    """Una tasca activa, una llista buida o un diàleg cancel·lat no arrenca el treballador."""
    env = student_env
    start = Mock()
    monkeypatch.setattr(env.controller._bulk_edit, "start", start)
    form = Mock(return_value=SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected))
    monkeypatch.setattr(env.controller, "bulk_dialog_factory", form)
    if reason == "busy":
        monkeypatch.setattr(env.controller._bulk_edit, "is_running", lambda: True)
    elif reason == "empty":
        env.services.students.delete(env.student.id)
    env.controller.bulk_edit()
    start.assert_not_called()
    if reason != "cancelled":
        form.assert_not_called()
    assert env.errors == env.messages == []


@pytest.mark.parametrize("failure", [False, True], ids=["cancel-lada", "error"])
def test_edicio_massiva_cancel_lada_o_fallida_no_refresca_com_si_fos_exit(
    student_env,
    monkeypatch,
    qtbot,
    failure,
):
    """El resultat asíncron conserva el detall i tanca el progrés sense anunciar èxit."""
    env = student_env
    form = SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        changes=lambda: [
            {
                "student_id": env.student.id,
                "name": "Laia Maria",
                "surnames": "Serra",
                "group_name": "4A",
            }
        ],
        effective_date=lambda: "2026-10-01",
    )
    monkeypatch.setattr(env.controller, "bulk_dialog_factory", lambda *args, **kwargs: form)

    def execute(changes, change_date, progress_callback, cancel_requested):
        progress_callback(0, len(changes))
        if failure:
            raise ValidationError("canvi invàlid")
        return SimpleNamespace(cancelled=True)

    monkeypatch.setattr(env.services.students, "bulk_update_with_worker_connection", execute)
    env.controller.bulk_edit()
    qtbot.waitUntil(lambda: not env.controller._bulk_edit.is_running(), timeout=5000)
    assert env.controller._bulk_edit.progress is None
    assert env.services.students.get_by_id(env.student.id) == env.student
    assert env.window.student_detail.current_student_id == env.student.id
    assert env.messages == []
    assert env.errors == (["canvi invàlid"] if failure else [])
    if not failure:
        assert "cancel·lada" in env.window.statusBar().currentMessage()
