import sys
from pathlib import Path

from PySide6.QtGui import QIcon


def asset_path(filename: str) -> Path:
    """Resol un recurs tant des del projecte com des d'un bundle PyInstaller."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).parents[2]))
    return bundle_root / "tutopy" / "ui" / "assets" / filename


def icon(filename: str) -> QIcon:
    return QIcon(str(asset_path(filename)))


def application_icon() -> QIcon:
    return icon("tutopy.svg")
