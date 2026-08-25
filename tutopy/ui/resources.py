"""Resolució de recursos visuals (icones i imatges) de la interfície.

Centralitza l'accés a la carpeta d'assets perquè funcioni tant en execució
des del codi font com empaquetada amb PyInstaller.
"""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialogButtonBox


ACTION_ICONS = {
    "add": "add.svg",
    "calendar": "calendar.svg",
    "cancel": "cancel.svg",
    "clear": "clear.svg",
    "confirm": "confirm.svg",
    "delete": "delete.svg",
    "deselect": "deselect.svg",
    "dropdown": "dropdown.svg",
    "edit": "edit.svg",
    "export": "export.svg",
    "image": "image.svg",
    "import": "import.svg",
    "open": "open.svg",
    "order": "order.svg",
    "refresh": "refresh.svg",
    "save": "save.svg",
    "select": "select.svg",
    "template": "template.svg",
}


def asset_path(filename: str) -> Path:
    """Resol un recurs tant des del projecte com des d'un bundle PyInstaller."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).parents[2]))
    return bundle_root / "tutopy" / "ui" / "assets" / filename


def icon(filename: str) -> QIcon:
    """Carrega una icona de la carpeta d'assets a partir del seu nom de fitxer."""
    return QIcon(str(asset_path(filename)))


def application_icon() -> QIcon:
    """Retorna la icona principal de l'aplicació Tutopy."""
    return icon("tutopy.svg")


def action_icon(action: str) -> QIcon:
    """Retorna una icona d'acció del catàleg visual de Tutopy."""
    try:
        return icon(ACTION_ICONS[action])
    except KeyError as error:
        raise ValueError(f"Acció d'icona desconeguda: {action}") from error


def set_button_icon(button, action: str) -> None:
    """Assigna a un botó una icona d'acció coherent."""
    button.setIcon(action_icon(action))


def set_dialog_button_icons(buttons: QDialogButtonBox) -> None:
    """Assigna icones coherents als botons estàndard d'un diàleg."""
    actions = {
        QDialogButtonBox.StandardButton.Save: "save",
        QDialogButtonBox.StandardButton.Ok: "confirm",
        QDialogButtonBox.StandardButton.Cancel: "cancel",
        QDialogButtonBox.StandardButton.Close: "cancel",
    }
    for standard_button, action in actions.items():
        button = buttons.button(standard_button)
        if button is not None:
            set_button_icon(button, action)
