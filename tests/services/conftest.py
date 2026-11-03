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
from tutopy.database.daos.student_photo_dao import PhotoDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.database.daos.annotation_dao import AnnotationDAO
from tutopy.services.photo_service import PhotoService

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8"
    b"\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


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
def photo_dao(db):
    """Retorna una instància de PhotoDAO."""
    return PhotoDAO(db.conn)


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


@pytest.fixture
def managed_photo(db, tmp_path):
    """Prepara una foto real al magatzem per verificar la gestió d'errors."""
    student = db.students.create(StudentNew("Laia", "Serra", "4A"))
    source = tmp_path / "original.png"
    source.write_bytes(MINIMAL_PNG)
    service = PhotoService(db.photos, db.students, storage_dir=tmp_path / "managed")
    photo = service.set_photo(student.id, str(source))
    return service, photo, source
