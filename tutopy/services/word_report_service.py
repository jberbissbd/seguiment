from collections import defaultdict
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.image.exceptions import UnrecognizedImageError
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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
        student, student_notes = self._student_and_notes(student_id)
        path = self._document_path(destination)
        categories = self.configuration.get_ordered_categories()
        document = self._new_document(student)
        self._add_courses(document, self._group_by_course(student_notes), categories)
        self._save_document(document, path)
        return path

    def _student_and_notes(self, student_id: int):
        student = self.students.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        student_notes = sorted(
            self.notes.get_by_student(student_id), key=lambda note: (note.date, note.id)
        )
        if not student_notes:
            raise ValidationError("L’alumne no té notes per exportar.")
        return student, student_notes

    @staticmethod
    def _document_path(destination: str | Path) -> Path:
        path = Path(destination)
        if path.suffix.lower() != ".docx":
            path = path.with_suffix(".docx")
        if not path.name:
            raise ValidationError("Cal indicar una destinació per a l’informe.")
        return path

    @staticmethod
    def _group_by_course(student_notes):
        by_course = defaultdict(list)
        for note in student_notes:
            by_course[note.course_id].append(note)
        return by_course

    def _new_document(self, student):
        document = Document()
        document.core_properties.title = self._safe_text(
            f"Informe de {student.filing_name}"
        )
        document.core_properties.subject = "Notes de seguiment"
        self._configure_page(document)
        self._add_student_header(
            document, student, self.configuration.get_header_image()
        )
        return document

    def _add_courses(self, document, by_course, categories) -> None:
        for index, (course_id, course_notes) in enumerate(sorted(
            by_course.items(), key=lambda item: self._course_name(item[0])
        )):
            if index:
                document.add_page_break()
            self._add_course(document, course_id, course_notes, categories)

    def _add_course(self, document, course_id, course_notes, categories) -> None:
        document.add_heading(self._course_name(course_id), level=1)
        notes_by_category = defaultdict(list)
        for note in course_notes:
            notes_by_category[note.category_id].append(note)
        for category in categories:
            category_notes = notes_by_category.get(category.id)
            if category_notes:
                self._add_category(document, category.name, category_notes)

    def _add_category(self, document, category_name: str, category_notes) -> None:
        document.add_heading(self._safe_text(category_name), level=2)
        table = document.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        self._configure_table_width(table)
        self._configure_table_header(table.rows[0].cells)
        for note in category_notes:
            self._add_note_row(table, note)

    @staticmethod
    def _configure_table_header(headers) -> None:
        headers[0].text = "Data"
        headers[1].text = "Anotació"
        for cell in headers:
            for run in cell.paragraphs[0].runs:
                run.bold = True

    def _add_note_row(self, table, note) -> None:
        cells = table.add_row().cells
        cells[0].text = date.fromisoformat(note.date).strftime("%d/%m/%Y")
        cells[1].text = self._safe_text(note.content)
        for cell, width in zip(cells, (Cm(3), Cm(14))):
            cell.width = width
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP

    @staticmethod
    def _save_document(document, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            document.save(path)
        except (OSError, ValueError) as error:
            raise ValidationError("No s’ha pogut desar l’informe.") from error

    @staticmethod
    def _configure_page(document) -> None:
        """Configura un A4 amb marges de 2 cm."""
        section = document.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2)
        section.right_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)

    def _add_student_header(self, document, student, header_image) -> None:
        """Afegeix el bloc inicial identificatiu i, opcionalment, un logotip."""
        if header_image:
            image_path = Path(header_image)
            if not image_path.is_file():
                raise ValidationError("No s’ha trobat la imatge de capçalera.")
            try:
                document.add_picture(str(image_path), width=Cm(5))
            except (OSError, ValueError, UnrecognizedImageError) as error:
                raise ValidationError("La imatge de capçalera no és vàlida.") from error
        document.add_heading(self._safe_text(student.filing_name), level=0)
        group = self._safe_text(student.group_name) or "Sense grup"
        paragraph = document.add_paragraph()
        paragraph.add_run("Grup: ").bold = True
        paragraph.add_run(group)

    @staticmethod
    def _configure_table_width(table) -> None:
        """Fixa la taula al 100% dels 17 cm disponibles entre marges."""
        table.autofit = False
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.columns[0].width = Cm(3)
        table.columns[1].width = Cm(14)
        table_width = table._tbl.tblPr.first_child_found_in("w:tblW")
        if table_width is None:
            table_width = OxmlElement("w:tblW")
            table._tbl.tblPr.append(table_width)
        table_width.set(qn("w:type"), "pct")
        table_width.set(qn("w:w"), "5000")
        for cell, width in zip(table.rows[0].cells, (Cm(3), Cm(14))):
            cell.width = width

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
