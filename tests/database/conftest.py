import pytest
from pathlib import Path

from tutopy.database.database import Database


@pytest.fixture(scope="module")
def directori_proves():
    return str(Path(__file__).parent / "test_data")


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("test_data")
    db_path = db_dir / "database.db"
    database_test = Database(str(db_path))
    database_test.connect()
    yield database_test
    database_test.close()
