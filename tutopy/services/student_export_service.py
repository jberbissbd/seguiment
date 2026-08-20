from pathlib import Path
import re
from datetime import date

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.report_file_service import ReportFileService
from tutopy.services.validation_service import ValidationService
from tutopy.models.reporting import BatchExportFailure, BatchExportResult


class StudentExportService:
    """Exporta l'informe i els documents d'un alumne en una carpeta ordenada."""

    def __init__(self, students: StudentDAO, documents: DocumentService,
                 courses: AcademicCourseDAO, report_files: ReportFileService):
        self.students = students
        self.documents = documents
        self.courses = courses
        self.report_files = report_files
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path,
                       report_format: str, include_terms: bool = False,
                       include_documents: bool = True,
                       folder_name: str | None = None) -> Path:
        student_id = self.validation.positive_id(student_id)
        student = self.students.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        self.report_files.get_format(report_format)
        base = Path(destination)
        if not base.name:
            raise ValidationError("Cal indicar una carpeta de destinació.")
        root = base / (folder_name or self._safe_name(student.filing_name, "Alumne"))
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ValidationError("No s’ha pogut crear la carpeta d’exportació.") from error

        report_path = root / f"informe.{report_format}"
        self.report_files.export_student(
            student_id, report_path, report_format, include_terms=include_terms
        )

        if include_documents:
            self._export_documents(student_id, root)
        return root

    def export_students(self, student_ids: list[int], destination: str | Path,
                        report_format: str, include_terms: bool = False,
                        include_documents: bool = False) -> BatchExportResult:
        base = self._validate_batch_request(student_ids, destination, report_format)
        batch_root = self._create_batch_root(base)
        failures = []
        used_folders = {}
        for student_id in student_ids:
            failure = self._export_batch_entry(
                student_id, batch_root, report_format, include_terms,
                include_documents, used_folders,
            )
            if failure is not None:
                failures.append(failure)
        return BatchExportResult(
            str(batch_root), len(student_ids) - len(failures), tuple(failures)
        )

    def _validate_batch_request(self, student_ids: list[int],
                                destination: str | Path,
                                report_format: str) -> Path:
        if not isinstance(student_ids, list) or not student_ids:
            raise ValidationError("Cal seleccionar almenys un alumne.")
        if any(isinstance(item, bool) or not isinstance(item, int) or item <= 0
               for item in student_ids):
            raise ValidationError("La selecció d’alumnes no és vàlida.")
        if len(student_ids) != len(set(student_ids)):
            raise ValidationError("La selecció d’alumnes conté duplicats.")
        self.report_files.get_format(report_format)
        base = Path(destination)
        if not base.name:
            raise ValidationError("Cal indicar una carpeta de destinació.")
        return base

    def _create_batch_root(self, base: Path) -> Path:
        batch_root = self._available_path(base / f"Informes {date.today().isoformat()}")
        try:
            batch_root.mkdir(parents=True)
        except OSError as error:
            raise ValidationError("No s’ha pogut crear la carpeta d’exportació.") from error
        return batch_root

    def _export_batch_entry(self, student_id: int, batch_root: Path,
                            report_format: str, include_terms: bool,
                            include_documents: bool,
                            used_folders: dict[str, int]) -> BatchExportFailure | None:
        student = None
        student_root = None
        try:
            student_id = self.validation.positive_id(student_id)
            student = self.students.get_by_id(student_id)
            if student is None:
                raise EntityNotFoundError("L’alumne seleccionat no existeix.")
            folder_name = self._next_student_folder(student.filing_name, used_folders)
            student_root = batch_root / folder_name
            self.export_student(
                student_id, batch_root, report_format,
                include_terms=include_terms,
                include_documents=include_documents,
                folder_name=folder_name,
            )
            return None
        except (ValidationError, EntityNotFoundError, OSError) as error:
            self._recover_documents(include_documents, student, student_root)
            return BatchExportFailure(
                student_id if isinstance(student_id, int) else 0,
                student.filing_name if student else f"ID {student_id}",
                str(error),
            )

    def _next_student_folder(self, filing_name: str,
                             used_folders: dict[str, int]) -> str:
        base_name = self._safe_name(filing_name, "Alumne")
        key = base_name.casefold()
        used_folders[key] = used_folders.get(key, 0) + 1
        if used_folders[key] == 1:
            return base_name
        return f"{base_name} ({used_folders[key]})"

    def _recover_documents(self, include_documents: bool, student,
                           student_root: Path | None) -> None:
        if not include_documents or student is None or student_root is None:
            return
        try:
            student_root.mkdir(parents=True, exist_ok=True)
            self._export_documents(student.id, student_root)
        except (ValidationError, EntityNotFoundError, OSError):
            pass

    def _export_documents(self, student_id: int, root: Path) -> None:
        used_names = {}
        courses_by_id = {course.id: course for course in self.courses.get_all()}
        for document in self.documents.get_by_student(student_id):
            course = courses_by_id.get(document.course_id)
            if course is None:
                raise ValidationError("Un document no té un curs acadèmic vàlid.")
            course_dir = root / self._safe_name(course.course, "Curs")
            course_dir.mkdir(parents=True, exist_ok=True)
            extension = Path(document.original_filename).suffix.lower()
            stem = self._safe_name(document.description or document.name, "Document")
            key = (course.id, stem.casefold(), extension)
            used_names[key] = used_names.get(key, 0) + 1
            suffix = f"_{used_names[key]}" if used_names[key] > 1 else ""
            self.documents.export_file(
                document.id, str(course_dir / f"{stem}{suffix}{extension}")
            )

    @staticmethod
    def _available_path(path: Path) -> Path:
        if not path.exists():
            return path
        index = 2
        while (candidate := path.with_name(f"{path.name} ({index})")).exists():
            index += 1
        return candidate

    @staticmethod
    def _safe_name(value: str, fallback: str) -> str:
        value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value).strip(" ._")
        return value[:120] or fallback
