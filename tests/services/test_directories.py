import os
from pathlib import Path
import pytest
from tutopy.services.directories import (
    _is_writable,
    get_project_root,
    get_executable_dir,
    get_app_data_dir,
    get_db_path,
    PROJECT_ROOT_MARKERS,
)


class TestIsWritable:
    """Tests per a la funció _is_writable."""

    def test_writable_directory(self, tmp_path):
        """Testa que un directori escribible retorna True."""
        writable_dir = tmp_path / "writable"
        writable_dir.mkdir()
        
        result = _is_writable(writable_dir)
        assert result is True

    def test_non_writable_directory(self, tmp_path):
        """Testa que un directori no escritible retorni False."""
        non_writable_dir = tmp_path / "non_writable"
        non_writable_dir.mkdir()
        
        original_mode = os.stat(non_writable_dir).st_mode
        os.chmod(non_writable_dir, 0o444)
        
        try:
            result = _is_writable(non_writable_dir)
            assert result is False
        finally:
            os.chmod(non_writable_dir, original_mode)

    def test_writable_path_object(self, tmp_path):
        """Testa que la funció accepta objectes Path."""
        writable_dir = tmp_path / "path_test"
        writable_dir.mkdir()
        
        result = _is_writable(Path(writable_dir))
        assert result is True

    def test_non_existent_directory_creates_and_checks(self, tmp_path):
        """Testa que un directori no existent es crea i es verifica."""
        non_existent_dir = tmp_path / "non_existent"
        result = _is_writable(non_existent_dir)
        assert result is True
        assert non_existent_dir.exists()


class TestGetProjectRoot:
    """Tests per a la funció get_project_root."""

    def test_returns_path(self):
        """Testa que retorna un objecte Path."""
        result = get_project_root()
        assert isinstance(result, Path)

    def test_contains_at_least_one_marker(self):
        """Testa que l'arrel del projecte conté almenys un dels marcadors."""
        root = get_project_root()
        markers_found = [marker for marker in PROJECT_ROOT_MARKERS if (root / marker).exists()]
        assert len(markers_found) > 0, f"No s'ha trobat cap marcador a {root}"

    def test_parent_is_not_root(self):
        """Testa que el directori pare no és el mateix que l'arrel."""
        root = get_project_root()
        assert root != root.parent


class TestGetExecutableDir:
    """Tests per a la funció get_executable_dir."""

    def test_returns_path(self):
        """Testa que retorna un objecte Path."""
        result = get_executable_dir()
        assert isinstance(result, Path)

    def test_equals_project_root(self):
        """Testa que get_executable_dir() retorna el mateix que get_project_root()."""
        assert get_executable_dir() == get_project_root()


class TestGetAppDataDir:
    """Tests per a la funció get_app_data_dir."""

    def test_returns_path(self):
        """Testa que retorna un objecte Path."""
        result = get_app_data_dir()
        assert isinstance(result, Path)

    def test_contains_app_name(self):
        """Testa que el path conté el nom de l'aplicació."""
        result = get_app_data_dir("test_app")
        assert "test_app" in str(result)

    def test_default_app_name(self):
        """Testa que el nom per defecte és estable encara que canviï el binari."""
        result = get_app_data_dir()
        assert result.name == "Tutopy"

    def test_linux_path_structure(self):
        """Testa l'estructura del path en Linux."""
        if os.name == "posix":
            result = get_app_data_dir()
            path_str = str(result)
            # En Linux hauria de contenir .local/share o XDG_DATA_HOME
            assert ".local/share" in path_str or "XDG_DATA_HOME" in os.environ


class TestGetDbPath:
    """Tests per a la funció get_db_path."""

    def test_returns_path(self, tmp_path, monkeypatch):
        """Testa que retorna un objecte Path."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        result = get_db_path()
        assert isinstance(result, Path)
        assert result.parent.exists()

    def test_default_db_name(self, tmp_path, monkeypatch):
        """Testa el nom per defecte de la base de dades de l'aplicació."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        result = get_db_path()
        assert result.name == "seguiment.db"

    def test_custom_db_name(self, tmp_path, monkeypatch):
        """Testa que accepta un nom de BD personalitzat."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        result = get_db_path("custom.db")
        assert result.name == "custom.db"

    def test_db_path_in_app_data(self, tmp_path, monkeypatch):
        """La BD no depèn de la carpeta del codi ni de l'executable."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        result = get_db_path()
        assert result.parent == tmp_path / "Tutopy"
