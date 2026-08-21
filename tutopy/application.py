from dataclasses import dataclass
from contextlib import contextmanager

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
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService
from tutopy.services.word_report_service import WordReportService
from tutopy.services.open_document_report_service import OpenDocumentReportService
from tutopy.services.report_file_service import ReportFileService
from tutopy.services.report_batch_loader import ReportBatchLoader
from tutopy.services.student_export_service import StudentExportService
from tutopy.services.directories import get_app_data_dir
from tutopy.services.statistics_service import StatisticsService
from tutopy.services.transfer_service import TransferService


@dataclass(frozen=True, slots=True)
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
    report_configuration: ReportConfigurationService
    spreadsheet_reports: SpreadsheetReportService
    word_reports: WordReportService
    open_document_reports: OpenDocumentReportService
    report_files: ReportFileService
    student_exports: StudentExportService
    statistics: StatisticsService
    transfers: TransferService


def create_services(
    database: Database, *, configure_worker_services: bool = True
) -> ServiceContainer:
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
    app_data_dir = get_app_data_dir()
    storage_dir = app_data_dir / "documents"
    report_configuration = ReportConfigurationService(
        database.report_configuration, database.academic_courses,
        database.categories, database.transaction,
        storage_dir=app_data_dir / "reporting",
    )
    report_batch_loader = ReportBatchLoader(
        database.students, database.notes, database.academic_courses,
        database.student_group_history, report_configuration,
    )
    spreadsheet_reports = SpreadsheetReportService(
        database.students, database.notes, database.academic_courses,
        database.student_group_history, report_configuration, report_batch_loader,
    )
    word_reports = WordReportService(
        database.students, database.notes, database.academic_courses,
        report_configuration, report_batch_loader,
    )
    open_document_reports = OpenDocumentReportService(
        database.students, database.notes, database.academic_courses,
        report_configuration, report_batch_loader,
    )
    report_files = ReportFileService(
        spreadsheet_reports, word_reports, open_document_reports
    )
    documents = DocumentService(
        database.documents, database.students, database.academic_courses,
        storage_dir=storage_dir,
    )
    container = ServiceContainer(
        students=students,
        notes=NoteService(
            database.notes,
            database.academic_courses,
            database.categories,
            database.students,
            database.transaction,
            database.student_group_history,
        ),
        categories=categories,
        academic_courses=AcademicCourseService(database.academic_courses),
        annotations=AnnotationService(database.annotations, database.students),
        contacts=ContactService(database.contacts, database.students),
        documents=documents,
        bulk_import=BulkImportService(
            students, categories, database.transaction,
        ),
        data_management=DataManagementService(
            database.data_management, database.documents,
            database.transaction, storage_dir,
        ),
        report_configuration=report_configuration,
        spreadsheet_reports=spreadsheet_reports,
        word_reports=word_reports,
        open_document_reports=open_document_reports,
        report_files=report_files,
        student_exports=StudentExportService(
            database.students, documents, database.academic_courses,
            report_files,
        ),
        statistics=StatisticsService(
            database.statistics, database.academic_courses, database.categories,
        ),
        transfers=TransferService(
            database.students, database.notes, database.categories,
            database.academic_courses, database.contacts, database.annotations,
            database.documents, database.student_group_history, documents,
            database.transaction,
        ),
    )
    if configure_worker_services:
        @contextmanager
        def transfer_worker_service():
            worker_database = Database(database.path).connect()
            try:
                worker = create_services(
                    worker_database, configure_worker_services=False
                )
                worker.documents.storage_dir = container.documents.storage_dir
                yield worker.transfers
            finally:
                worker_database.close()

        container.transfers.worker_service_factory = transfer_worker_service

        @contextmanager
        def student_worker_service():
            worker_database = Database(database.path).connect()
            try:
                worker = create_services(
                    worker_database, configure_worker_services=False
                )
                yield worker.students
            finally:
                worker_database.close()

        container.students.worker_service_factory = student_worker_service
    return container
