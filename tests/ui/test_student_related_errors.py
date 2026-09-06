"""Proves de persistència, cancel·lació i errors de les dades associades."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QFileDialog


def test_edicio_actualitza_dades_i_preserva_identitat(
    student_related_env, monkeypatch, related_kind
):
    """Editar metadades conserva l'alumne, l'identificador i el fitxer original."""
    values = {
        "annotation": {"content": "Nou descriptor"},
        "contact": {"name": "Joan", "description": "Pare", "phone": "", "email": ""},
        "document": {"name": "Nou informe", "description": "Anual", "date": "2026-10-01"},
    }
    form = SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        value=lambda: "Nou descriptor",
        values=lambda: values[related_kind],
    )
    monkeypatch.setattr(
        student_related_env.controller, f"{related_kind}_dialog", lambda **kwargs: form
    )
    original = getattr(student_related_env, related_kind)
    getattr(student_related_env.controller, f"edit_{related_kind}")(original.id)
    service = getattr(student_related_env.services, f"{related_kind}s")
    updated = service.get_by_id(original.id)
    assert updated.student_id == original.student_id
    for field, value in values[related_kind].items():
        assert getattr(updated, field) == value
    if related_kind == "document":
        assert updated.file_path == original.file_path
        assert updated.uuid_filename == original.uuid_filename
        assert Path(updated.file_path).read_text() == "Informe original"
        assert updated.course_id != original.course_id
    assert student_related_env.errors == []
    assert "actualitzat" in student_related_env.window.statusBar().currentMessage()


@pytest.mark.parametrize("operation", ["create", "edit"])
def test_cancel_lar_formulari_no_modifica_dades(
    student_related_env, monkeypatch, related_kind, operation
):
    """Cancel·lar tant la creació com l'edició deixa el registre intacte."""
    form = SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected)
    monkeypatch.setattr(
        student_related_env.controller, f"{related_kind}_dialog", lambda **kwargs: form
    )
    action = getattr(student_related_env.controller, f"{operation}_{related_kind}")
    action(*([getattr(student_related_env, related_kind).id] if operation == "edit" else []))
    assert getattr(student_related_env.services, f"{related_kind}s").get_by_student(
        student_related_env.student.id
    ) == [getattr(student_related_env, related_kind)]
    assert student_related_env.errors == []


def test_sense_alumne_no_obre_formularis(student_related_env, monkeypatch, related_kind):
    """La creació sense context no obre diàlegs ni refresca altres alumnes."""

    def unexpected(**kwargs):
        pytest.fail("No s'ha d'obrir un formulari sense alumne")

    student_related_env.controller.student_id = None
    monkeypatch.setattr(student_related_env.controller, f"{related_kind}_dialog", unexpected)
    student_related_env.controller.refresh_all()
    getattr(student_related_env.controller, f"create_{related_kind}")()
    assert getattr(student_related_env.services, f"{related_kind}s").get_by_student(
        student_related_env.student.id
    ) == [getattr(student_related_env, related_kind)]


@pytest.mark.parametrize(
    "action",
    [
        "edit_annotation",
        "edit_contact",
        "edit_document",
        "open_document",
        "export_document",
    ],
)
def test_entitat_inexistent_mostra_error(student_related_env, action):
    """Accedir a un registre eliminat informa de l'error sense continuar l'acció."""
    getattr(student_related_env.controller, action)(9999)
    assert len(student_related_env.errors) == 1
    assert "no existeix" in student_related_env.errors[0]


@pytest.mark.parametrize("confirmed", [False, True])
def test_eliminacio_respecta_confirmacio(student_related_env, monkeypatch, related_kind, confirmed):
    """Només una confirmació afirmativa elimina les dades i refresca la vista."""
    monkeypatch.setattr(student_related_env.controller, "confirm_delete", lambda _name: confirmed)
    getattr(student_related_env.controller, f"delete_{related_kind}")(
        getattr(student_related_env, related_kind).id
    )
    records = getattr(student_related_env.services, f"{related_kind}s").get_by_student(
        student_related_env.student.id
    )
    assert records == ([] if confirmed else [getattr(student_related_env, related_kind)])
    assert student_related_env.errors == []


def test_error_de_validacio_no_publica_exit(student_related_env, monkeypatch):
    """Un descriptor buit manté el valor anterior i informa de la validació."""
    form = SimpleNamespace(exec=lambda: QDialog.DialogCode.Accepted, value=lambda: " ")
    monkeypatch.setattr(student_related_env.controller, "annotation_dialog", lambda **kwargs: form)
    student_related_env.controller.edit_annotation(student_related_env.annotation.id)
    assert (
        student_related_env.services.annotations.get_by_id(student_related_env.annotation.id)
        == student_related_env.annotation
    )
    assert len(student_related_env.errors) == 1
    assert "actualitzat" not in student_related_env.window.statusBar().currentMessage()


def test_error_netejant_document_refresca_registre_eliminat(student_related_env, monkeypatch):
    """L'avís de fitxer residual no deixa el document eliminat visible a la taula."""
    unlink = Path.unlink

    def fail_quarantine(path, *args, **kwargs):
        if path.name.endswith(".deleting"):
            raise PermissionError("fitxer bloquejat")
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_quarantine)
    student_related_env.controller.delete_document(student_related_env.document.id)
    assert (
        student_related_env.services.documents.get_by_student(student_related_env.student.id) == []
    )
    assert student_related_env.window.student_detail.document_tab.table.rowCount() == 0
    assert len(student_related_env.errors) == 1
    assert "no s'ha pogut esborrar" in student_related_env.errors[0]


def test_obertura_sense_aplicacio_associada_informa(student_related_env, monkeypatch):
    """La negativa del sistema a obrir el fitxer es comunica a l'usuari."""
    opened = []
    monkeypatch.setattr(
        QDesktopServices, "openUrl", lambda url: opened.append(url.toLocalFile()) or False
    )
    student_related_env.controller.open_document(student_related_env.document.id)
    assert opened == [student_related_env.document.file_path]
    assert student_related_env.errors == ["No s'ha trobat cap aplicació per obrir el document."]


@pytest.mark.parametrize("cancelled", [False, True])
def test_exportacio_utilitza_destinacio_o_respecta_cancel_lacio(
    student_related_env,
    monkeypatch,
    tmp_path,
    cancelled,
):
    """El diàleg de fitxer cancel·lat no copia ni publica un missatge d'èxit."""
    destination = tmp_path / "copia.txt"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: ("" if cancelled else str(destination), ""),
    )
    student_related_env.controller.export_document(student_related_env.document.id)
    assert destination.exists() is not cancelled
    if not cancelled:
        assert destination.read_text() == "Informe original"
    assert student_related_env.errors == []
