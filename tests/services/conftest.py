import pytest
from pathlib import Path
from tutopy.database.database import Database
from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO


@pytest.fixture(scope="function")
def db(tmp_path_factory):
    """Crea una base de dades temporal per a cada test."""
    db_dir = tmp_path_factory.mktemp("test_data")
    db_path = db_dir / "database.db"
    database_test = Database(str(db_path))
    database_test.connect()
    yield database_test
    database_test.close()


@pytest.fixture
def note_dao(db):
    """Retorna una instància de NoteDAO."""
    return NoteDAO(db.conn, db.academic_courses)


@pytest.fixture
def academic_course_dao(db):
    """Retorna una instància de AcademicCourseDAO."""
    return AcademicCourseDAO(db.conn)


@pytest.fixture
def category_dao(db):
    """Retorna una instància de CategoryDAO."""
    return CategoryDAO(db.conn)
