import os
from pathlib import Path
import pytest
from tutopy.services.directories import _is_writable


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
