import os
import sys
from pathlib import Path

APP_NAME = "Tutopy"

# Marcadors per identificar l'arrel del projecte
PROJECT_ROOT_MARKERS = ["main.py", "requirements.txt", "pyproject.toml", ".git"]


def get_project_root() -> Path:
    """Retorna el directori arrel del projecte.

    En mode desenvolupament, busca un dels fitxers marcadors (main.py, requirements.txt, etc.)
    pujant pel sistema de fitxers. En mode PyInstaller, retorna el directori de l'executable.
    Funciona independentment de la profunditat del fitxer en el sistema de fitxers.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    # Buscar marcadors de l'arrel del projecte
    current_dir = Path(__file__).parent
    while current_dir != current_dir.parent:  # Parar quan s'arribi a l'arrel del sistema
        for marker in PROJECT_ROOT_MARKERS:
            if (current_dir / marker).exists():
                return current_dir
        current_dir = current_dir.parent

    # Fallback: tornar el directori pare del fitxer actual
    return Path(__file__).parent


def get_executable_dir() -> Path:
    """Retorna la carpeta on es troba l'executable (o l'arrel del projecte en dev).

    - PyInstaller (--onefile): carpeta de l'executable empaquetat
    - PyInstaller (--onedir):  carpeta del bundle
    - Desenvolupament:         arrel del projecte
    """
    return get_project_root()


def get_app_data_dir(app_name: str = APP_NAME) -> Path:
    """Retorna el directori estàndard del SO per dades d'aplicació.

    Windows: %LOCALAPPDATA%/%app_name% o %APPDATA%/%app_name%
    macOS: ~/Library/Application Support/%app_name%
    Linux/Unix: ~/.local/share/%app_name% (o $XDG_DATA_HOME/%app_name%)
    """
    if sys.platform == "win32":
        # Windows: prioritzar LOCALAPPDATA sobre APPDATA
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / app_name
        app_data = os.environ.get("APPDATA")
        if app_data:
            return Path(app_data) / app_name
    elif sys.platform == "darwin":
        # macOS
        return Path.home() / "Library" / "Application Support" / app_name
    else:
        # Linux/Unix
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            return Path(xdg_data_home) / app_name
        return Path.home() / ".local" / "share" / app_name

    # Fallback si cap variable d'entorn està disponible
    return Path.home() / f".{app_name}"


def get_db_path(db_name: str = "seguiment.db") -> Path:
    """Retorna una ruta persistent, independent de la ubicació de l'executable."""
    app_data_dir = get_app_data_dir()
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / db_name


def _is_writable(path: Path) -> bool:
    """Comprova si el directori existeix i és escribible en qualsevol plataforma."""
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            return False
    test_file = path / ".write_test"
    try:
        test_file.touch(exist_ok=False)
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False
