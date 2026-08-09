#!/usr/bin/env python3
"""
Punt d'entrada principal de l'aplicació Seguiment d'Alumnes.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from tutopy.ui.main_window import MainWindow
from tutopy.ui.styles import apply_global_style, set_high_dpi
from tutopy.services.directories import get_db_path


VERSION = "0.0.1"


def get_db_path_for_app() -> Path:
    """Obté el path de la base de dades per a l'aplicació."""
    return get_db_path()


def create_application() -> QApplication:
    """Crea i configura l'aplicació Qt."""
    app = QApplication(sys.argv)
    
    # Configurar HighDPI
    set_high_dpi(app)
    
    # Aplicar estils globals
    apply_global_style(app)
    
    # Configurar informació de l'aplicació
    app.setApplicationName("Seguiment d'Alumnes")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("Tutopy")
    
    # Configurar font
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    return app


def main():
    """Funció principal de l'aplicació."""
    app = create_application()
    
    try:
        # Obtenir el path de la base de dades
        db_path = get_db_path_for_app()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear i mostrar la finestra principal
        window = MainWindow(str(db_path))
        window.setWindowTitle(f"Seguiment d'Alumnes - v{VERSION}")
        window.show()
        
        return app.exec()
        
    except Exception as e:
        from PySide6.QtWidgets import QMessageBox
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText("S'ha produït un error al iniciar l'aplicació:")
        error_box.setInformativeText(str(e))
        error_box.exec()
        return 1


if __name__ == "__main__":
    sys.exit(main())
