"""Connexions, repositoris i documents temporals compartits entre serveis."""

import pytest
from tutopy.database.database import Database
from tutopy.models.messaging import StudentNew
from tutopy.services.document_service import DocumentService
from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.database.daos.annotation_dao import AnnotationDAO


@pytest.fixture
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
    return NoteDAO(db.conn)


@pytest.fixture
def academic_course_dao(db):
    """Retorna una instància de AcademicCourseDAO."""
    return AcademicCourseDAO(db.conn)


@pytest.fixture
def category_dao(db):
    """Retorna una instància de CategoryDAO."""
    return CategoryDAO(db.conn)


@pytest.fixture
def student_dao(db):
    """Retorna una instància de StudentDAO."""
    return StudentDAO(db.conn)


@pytest.fixture
def contact_dao(db):
    """Retorna una instància de ContactDAO."""
    return ContactDAO(db.conn)


@pytest.fixture
def document_dao(db):
    """Retorna una instància de DocumentDAO."""
    return DocumentDAO(db.conn)


@pytest.fixture
def group_history_dao(db):
    """Retorna una instància de StudentGroupHistoryDAO."""
    return StudentGroupHistoryDAO(db.conn)


@pytest.fixture
def annotation_dao(db):
    """Retorna una instància de AnnotationDAO."""
    return AnnotationDAO(db.conn)


@pytest.fixture
def managed_document(db, tmp_path):
    """Prepara un document real al magatzem per verificar la gestió d'errors."""
    student = db.students.create(StudentNew("Laia", "Serra", "4A"))
    source = tmp_path / "original.txt"
    source.write_text("Document original", encoding="utf-8")
    service = DocumentService(
        db.documents, db.students, db.academic_courses, storage_dir=tmp_path / "managed",
    )
    document = service.import_file(student.id, "Informe", "", str(source), "2026-02-01")
    return service, document, source
