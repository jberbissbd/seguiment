from collections import defaultdict
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Cm

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.validation_service import ValidationService


class WordReportService:
    """Genera un informe DOCX de les notes de seguiment d'un alumne."""

    def __init__(self, students: StudentDAO, notes: NoteDAO,
                 courses: AcademicCourseDAO,
                 configuration: ReportConfigurationService):
        self.students = students
        self.notes = notes
        self.courses = courses
        self.configuration = configuration
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path) -> Path:
        student_id = self.validation.positive_id(student_id)
        student = self.students.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        student_notes = sorted(
            self.notes.get_by_student(student_id), key=lambda note: (note.date, note.id)
        )
        if not student_notes:
            raise ValidationError("L’alumne no té notes per exportar.")

        path = Path(destination)
        if path.suffix.lower() != ".docx":
            path = path.with_suffix(".docx")
        if not path.name:
            raise ValidationError("Cal indicar una destinació per a l’informe.")

        categories = self.configuration.get_ordered_categories()
        by_course = defaultdict(list)
        for note in student_notes:
            by_course[note.course_id].append(note)

        document = Document()
        document.core_properties.title = self._safe_text(f"Informe de {student.full_name}")
        document.core_properties.subject = "Notes de seguiment"
        for index, (course_id, course_notes) in enumerate(sorted(
            by_course.items(), key=lambda item: self._course_name(item[0])
        )):
            if index:
                document.add_page_break()
            document.add_heading(self._course_name(course_id), level=1)
            notes_by_category = defaultdict(list)
            for note in course_notes:
                notes_by_category[note.category_id].append(note)
            for category in categories:
                category_notes = notes_by_category.get(category.id)
                if not category_notes:
                    continue
                document.add_heading(self._safe_text(category.name), level=2)
                table = document.add_table(rows=1, cols=2)
                table.style = "Table Grid"
                table.columns[0].width = Cm(3)
                table.columns[1].width = Cm(13)
                headers = table.rows[0].cells
                headers[0].text = "Data"
                headers[1].text = "Anotació"
                for cell in headers:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
                for note in category_notes:
                    cells = table.add_row().cells
                    cells[0].text = date.fromisoformat(note.date).strftime("%d/%m/%Y")
                    cells[1].text = self._safe_text(note.content)
                    for cell in cells:
                        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            document.save(path)
        except (OSError, ValueError) as error:
            raise ValidationError("No s’ha pogut desar l’informe.") from error
        return path

    def _course_name(self, course_id: int) -> str:
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise ValidationError("Una nota fa referència a un curs acadèmic inexistent.")
        return course.course

    @staticmethod
    def _safe_text(value) -> str:
        """Elimina els controls que XML no admet, conservant salts i tabuladors."""
        text = "" if value is None else str(value)
        return "".join(character for character in text if (
            character in "\t\n\r"
            or 0x20 <= ord(character) <= 0xD7FF
            or 0xE000 <= ord(character) <= 0xFFFD
            or 0x10000 <= ord(character) <= 0x10FFFF
        ))
