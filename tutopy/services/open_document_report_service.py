from collections import defaultdict
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from odf import draw, style, table, text
from odf.opendocument import OpenDocumentText
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.validation_service import ValidationService


class OpenDocumentReportService:
    """Genera els informes de text oberts (ODT) i PDF sense eines externes."""

    def __init__(self, students, notes, courses, configuration):
        self.students = students
        self.notes = notes
        self.courses = courses
        self.configuration = configuration
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path,
                       report_format: str) -> Path:
        if report_format not in {"odt", "pdf"}:
            raise ValidationError("El format del document no és vàlid.")
        student_id = self.validation.positive_id(student_id)
        student = self.students.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        notes = sorted(
            self.notes.get_by_student(student_id), key=lambda item: (item.date, item.id)
        )
        if not notes:
            raise ValidationError("L’alumne no té notes per exportar.")
        path = self._destination(destination, report_format)
        courses = self._report_courses(notes)
        categories = self.configuration.get_ordered_categories()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if report_format == "odt":
                self._save_odt(path, student, courses, categories)
            else:
                self._save_pdf(path, student, courses, categories)
        except (OSError, ValueError) as error:
            raise ValidationError("No s’ha pogut desar l’informe.") from error
        return path

    @staticmethod
    def _destination(destination, extension):
        path = Path(destination)
        if path.suffix.lower() != f".{extension}":
            path = path.with_suffix(f".{extension}")
        if not path.name:
            raise ValidationError("Cal indicar una destinació per a l’informe.")
        return path

    def _report_courses(self, notes):
        grouped = defaultdict(list)
        for note in notes:
            grouped[note.course_id].append(note)
        result = []
        for course_id, course_notes in grouped.items():
            course = self.courses.get_by_id(course_id)
            if course is None:
                raise ValidationError("Una nota fa referència a un curs acadèmic inexistent.")
            result.append((course.course, course_notes))
        return sorted(result, key=lambda item: item[0])

    def _save_odt(self, path, student, courses, categories):
        document = OpenDocumentText()
        title_style = style.Style(name="TutopyTitle", family="paragraph")
        title_style.addElement(style.TextProperties(fontsize="20pt", fontweight="bold"))
        document.styles.addElement(title_style)
        heading_style = style.Style(name="TutopyHeading", family="paragraph")
        heading_style.addElement(style.TextProperties(fontsize="16pt", fontweight="bold"))
        document.styles.addElement(heading_style)
        category_style = style.Style(name="TutopyCategory", family="paragraph")
        category_style.addElement(style.TextProperties(fontsize="13pt", fontweight="bold"))
        document.styles.addElement(category_style)
        page_break_style = style.Style(name="TutopyPageBreak", family="paragraph")
        page_break_style.addElement(style.ParagraphProperties(breakbefore="page"))
        document.automaticstyles.addElement(page_break_style)
        header_style = style.Style(name="TutopyTableHeader", family="table-cell")
        header_style.addElement(style.TextProperties(fontweight="bold"))
        document.styles.addElement(header_style)

        logo = self.configuration.get_header_image()
        if logo:
            href = document.addPicture(str(logo))
            frame = draw.Frame(width="5cm", height="2cm", anchortype="paragraph")
            frame.addElement(draw.Image(href=href))
            paragraph = text.P()
            paragraph.addElement(frame)
            document.text.addElement(paragraph)
        document.text.addElement(text.P(stylename=title_style, text=self._safe(student.filing_name)))
        document.text.addElement(text.P(text=f"Grup: {self._safe(student.group_name) or 'Sense grup'}"))
        document.text.addElement(text.P(
            text=f"Data d’exportació: {date.today().strftime('%d/%m/%Y')}"
        ))
        for course_index, (course_name, course_notes) in enumerate(courses):
            if course_index:
                document.text.addElement(text.P(stylename=page_break_style))
            document.text.addElement(text.P(stylename=heading_style, text=self._safe(course_name)))
            by_category = defaultdict(list)
            for note in course_notes:
                by_category[note.category_id].append(note)
            for category in categories:
                category_notes = by_category.get(category.id)
                if not category_notes:
                    continue
                document.text.addElement(text.P(
                    stylename=category_style, text=self._safe(category.name)
                ))
                report_table = table.Table()
                header = table.TableRow()
                for value in ("Data", "Anotació"):
                    cell = table.TableCell(stylename=header_style)
                    cell.addElement(text.P(text=value))
                    header.addElement(cell)
                report_table.addElement(header)
                for note in category_notes:
                    row = table.TableRow()
                    for value in (
                        date.fromisoformat(note.date).strftime("%d/%m/%Y"),
                        self._safe(note.content),
                    ):
                        cell = table.TableCell()
                        cell.addElement(text.P(text=value))
                        row.addElement(cell)
                    report_table.addElement(row)
                document.text.addElement(report_table)
        document.save(str(path), addsuffix=False)

    def _save_pdf(self, path, student, courses, categories):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="TutopyTitle", parent=styles["Title"], alignment=TA_CENTER,
            spaceAfter=10,
        ))
        story = []
        logo = self.configuration.get_header_image()
        if logo:
            story.extend((Image(str(logo), width=5 * cm, height=2 * cm, kind="proportional"),
                          Spacer(1, 0.25 * cm)))
        story.append(Paragraph(escape(self._safe(student.filing_name)), styles["TutopyTitle"]))
        story.append(Paragraph(
            f"<b>Grup:</b> {escape(self._safe(student.group_name) or 'Sense grup')}",
            styles["BodyText"],
        ))
        story.append(Paragraph(
            f"<b>Data d’exportació:</b> {date.today().strftime('%d/%m/%Y')}",
            styles["BodyText"],
        ))
        for course_index, (course_name, course_notes) in enumerate(courses):
            if course_index:
                story.append(PageBreak())
            story.append(Paragraph(escape(self._safe(course_name)), styles["Heading1"]))
            by_category = defaultdict(list)
            for note in course_notes:
                by_category[note.category_id].append(note)
            for category in categories:
                category_notes = by_category.get(category.id)
                if not category_notes:
                    continue
                story.append(Paragraph(escape(self._safe(category.name)), styles["Heading2"]))
                rows = [[Paragraph("<b>Data</b>", styles["BodyText"]),
                         Paragraph("<b>Anotació</b>", styles["BodyText"])]]
                rows.extend([
                    [date.fromisoformat(note.date).strftime("%d/%m/%Y"),
                     Paragraph(escape(self._safe(note.content)).replace("\n", "<br/>"),
                               styles["BodyText"])]
                    for note in category_notes
                ])
                report_table = Table(rows, colWidths=(3 * cm, 14 * cm), repeatRows=1)
                report_table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.extend((report_table, Spacer(1, 0.35 * cm)))
        pdf = SimpleDocTemplate(
            str(path), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
            title=f"Informe de {self._safe(student.filing_name)}",
            subject="Notes de seguiment",
        )
        pdf.build(story)

    @staticmethod
    def _safe(value):
        value = "" if value is None else str(value)
        return "".join(character for character in value if (
            character in "\t\n\r" or 0x20 <= ord(character) <= 0xD7FF
            or 0xE000 <= ord(character) <= 0xFFFD
            or 0x10000 <= ord(character) <= 0x10FFFF
        ))
