from dataclasses import dataclass

from tutopy.database.database import Database
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.annotation_service import AnnotationService
from tutopy.services.category_service import CategoryService
from tutopy.services.contact_service import ContactService
from tutopy.services.document_service import DocumentService
from tutopy.services.note_service import NoteService
from tutopy.services.student_service import StudentService
from tutopy.services.bulk_import_service import BulkImportService
from tutopy.services.data_management_service import DataManagementService
from tutopy.services.directories import get_app_data_dir


@dataclass(frozen=True)
class ServiceContainer:
    """Serveis disponibles per als controladors de l'aplicació."""

    students: StudentService
    notes: NoteService
    categories: CategoryService
    academic_courses: AcademicCourseService
    annotations: AnnotationService
    contacts: ContactService
    documents: DocumentService
    bulk_import: BulkImportService
    data_management: DataManagementService


def create_services(database: Database) -> ServiceContainer:
    """Construeix la capa de negoci sense exposar DAOs a la UI."""
    if database.conn is None:
        raise RuntimeError("La base de dades ha d'estar connectada.")

    students = StudentService(
            database.students,
            database.contacts,
            database.documents,
            database.student_group_history,
            database.academic_courses,
            database.transaction,
        )
    categories = CategoryService(database.categories)
    storage_dir = get_app_data_dir() / "documents"
    return ServiceContainer(
        students=students,
        notes=NoteService(
            database.notes,
            database.academic_courses,
            database.categories,
            database.students,
            database.transaction,
        ),
        categories=categories,
        academic_courses=AcademicCourseService(database.academic_courses),
        annotations=AnnotationService(database.annotations, database.students),
        contacts=ContactService(database.contacts, database.students),
        documents=DocumentService(
            database.documents,
            database.students,
            storage_dir=storage_dir,
        ),
        bulk_import=BulkImportService(
            students, categories, database.transaction,
        ),
        data_management=DataManagementService(
            database.data_management, database.documents,
            database.transaction, storage_dir,
        ),
    )
