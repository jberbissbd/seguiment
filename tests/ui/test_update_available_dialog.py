from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from tutopy.ui.dialogs.update_available_dialog import UpdateAvailableDialog


def _open_button(dialog):
    buttons = dialog.findChild(QDialogButtonBox)
    return next(
        button for button in buttons.buttons()
        if "descàrrega" in button.text()
    )


def test_boto_obre_la_pagina_de_descarrega(qtbot, monkeypatch):
    opened = []
    monkeypatch.setattr(
        QDesktopServices, "openUrl", lambda url: opened.append(url.toString())
    )
    dialog = UpdateAvailableDialog("1.4.0", "https://example.test/releases/v1.4.0")
    qtbot.addWidget(dialog)

    _open_button(dialog).click()

    assert opened == ["https://example.test/releases/v1.4.0"]


def test_tancar_accepta_el_dialeg_sense_obrir_cap_url(qtbot, monkeypatch):
    opened = []
    monkeypatch.setattr(
        QDesktopServices, "openUrl", lambda url: opened.append(url.toString())
    )
    dialog = UpdateAvailableDialog("1.4.0", "https://example.test/releases/v1.4.0")
    qtbot.addWidget(dialog)
    buttons = dialog.findChild(QDialogButtonBox)

    buttons.button(QDialogButtonBox.StandardButton.Close).click()

    assert opened == []
    assert dialog.result() == QDialog.DialogCode.Accepted
