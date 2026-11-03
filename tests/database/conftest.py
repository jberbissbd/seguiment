"""Fixtures compartides pels tests de la base de dades."""

import pytest
from pathlib import Path

from tutopy.database.database import Database


@pytest.fixture(scope="module")
def directori_proves():
    """Retorna la ruta del directori de dades de prova."""
    return str(Path(__file__).parent / "test_data")


@pytest.fixture
def db(tmp_path_factory):
    """Connecta una base de dades SQLite temporal per a la prova."""
    db_dir = tmp_path_factory.mktemp("test_data")
    db_path = db_dir / "database.db"
    database_test = Database(str(db_path))
    database_test.connect()
    yield database_test
    database_test.close()
