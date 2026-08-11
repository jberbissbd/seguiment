from pathlib import Path
import re

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService
from tutopy.services.word_report_service import WordReportService
from tutopy.services.validation_service import ValidationService


class StudentExportService:
    """Exporta l'informe i els documents d'un alumne en una carpeta ordenada."""

    def __init__(self, students: StudentDAO, documents: DocumentService,
                 courses: AcademicCourseDAO, spreadsheets: SpreadsheetReportService,
                 word_reports: WordReportService):
        self.students = students
        self.documents = documents
        self.courses = courses
        self.spreadsheets = spreadsheets
        self.word_reports = word_reports
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path,
                       report_format: str, include_terms: bool = False) -> Path:
        student_id = self.validation.positive_id(student_id)
        student = self.students.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        if report_format not in {"xlsx", "docx"}:
            raise ValidationError("El format de l’informe no és vàlid.")
        base = Path(destination)
        if not base.name:
            raise ValidationError("Cal indicar una carpeta de destinació.")
        root = base / self._safe_name(student.filing_name, "Alumne")
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ValidationError("No s’ha pogut crear la carpeta d’exportació.") from error

        report_path = root / f"informe.{report_format}"
        if report_format == "docx":
            self.word_reports.export_student(student_id, report_path)
        else:
            self.spreadsheets.export_student(
                student_id, report_path, include_terms=include_terms
            )

        used_names = {}
        for document in self.documents.get_by_student(student_id):
            course = self.courses.get_by_id(document.course_id) if document.course_id else None
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
        return root

    @staticmethod
    def _safe_name(value: str, fallback: str) -> str:
        value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value).strip(" ._")
        return value[:120] or fallback
