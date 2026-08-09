"""
Paquet UI de l'aplicació Seguiment d'Alumnes.

Conté tots els components de la interfície d'usuari.
"""

from .main_window import MainWindow
from .styles import apply_global_style, set_high_dpi, get_central_style

__all__ = [
    "MainWindow",
    "apply_global_style",
    "set_high_dpi",
    "get_central_style",
]
