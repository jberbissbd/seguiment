import sys

from pathlib import Path


def get_executable_dir() -> Path:
    """
    Retorna la carpeta on es troba l'executable (o main.py en dev).
    - PyInstaller (--onefile): carpeta de l'executable empaquetado
    - PyInstaller (--onedir):  carpeta del bundle
    - Desenvolupament:         carpeta de main.py
    """
    if getattr(sys, "frozen", False):
        # Estem dins d'un executable PyInstaller
        return Path(sys.executable).parent
    else:
        # Estem en mode desenvolupament
        return Path(__file__).parent.parent.parent  # arrel del projecte

def get_db_path() -> Path:
    """
    Intenta posar la BD al costat de l'executable.
    Si no hi ha permisos d'escriptura, cau al directori estàndard del SO.
    """
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        if _is_writable(exe_dir):
            return exe_dir / "app.db"
        else:
            # fallback segur si no hi ha permisos (ex: Program Files)
            return get_app_data_dir() / "app.db"
    else:
        return get_project_root() / "app.db"


def _is_writable(path: Path) -> bool:
    """Comprova si el directori és escribible en qualsevol plataforma."""
    test_file = path / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False