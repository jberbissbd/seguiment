"""Generació de l'informe XLSX de les notes de seguiment d'un alumne."""

from collections import defaultdict
from datetime import date
from pathlib import Path
import unicodedata

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.validation_service import ValidationService


class SpreadsheetReportService:
    """Genera l'informe XLSX de les notes de seguiment d'un alumne."""

    EXCEL_CELL_LIMIT = 32_767

    def __init__(self, students: StudentDAO, notes: NoteDAO,
                 courses: AcademicCourseDAO, group_history: StudentGroupHistoryDAO,
                 configuration: ReportConfigurationService, batch_loader=None):
        """Rep els repositoris de domini i, opcionalment, el carregador de lots."""
        self.students = students
        self.notes = notes
        self.courses = courses
        self.group_history = group_history
        self.configuration = configuration
        self.batch_loader = batch_loader
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path,
                       include_terms: bool = False) -> Path:
        """Exporta l'informe XLSX d'un únic alumne.

        Args:
            student_id: ID de l'alumne.
            destination: Ruta de destinació (l'extensió es normalitza a `.xlsx`).
            include_terms: Si cal afegir una columna amb el trimestre de
                cada nota, segons la configuració de trimestres del grup.

        Returns:
            Ruta final del fitxer generat.

        Raises:
            ValidationError: Si l'alumne no té notes per exportar.
            EntityNotFoundError: Si l'alumne no existeix.
        """
        student_id = self.validation.positive_id(student_id)
        data = self.prepare_students([student_id], include_terms=include_terms)
        return self.export_prepared(student_id, destination, data, include_terms)

    def prepare_students(self, student_ids: list[int], include_terms: bool = False):
        """Carrega una vegada les dades compartides dels informes XLSX."""
        return self.batch_loader.load(
            student_ids, include_histories=True, include_terms=include_terms
        )

    def export_prepared(
        self, student_id: int, destination: str | Path, data,
        include_terms: bool = False,
    ) -> Path:
        """Genera un XLSX a partir d'un snapshot carregat prèviament."""
        from openpyxl import Workbook

        student = data.students.get(student_id)
        if student is None:
            raise EntityNotFoundError("L’alumne seleccionat no existeix.")
        student_notes = sorted(
            data.notes[student_id], key=lambda note: (note.date, note.id)
        )
        if not student_notes:
            raise ValidationError("L’alumne no té notes per exportar.")
        path = Path(destination)
        if path.suffix.lower() != ".xlsx":
            path = path.with_suffix(".xlsx")
        if not path.name:
            raise ValidationError("Cal indicar una destinació per a l’informe.")

        categories = data.categories
        histories = data.histories[student_id]
        by_course = defaultdict(list)
        for note in student_notes:
            by_course[note.course_id].append(note)
        course_names = self._course_names(by_course, data.course_names)

        workbook = Workbook()
        workbook.remove(workbook.active)
        for course_id, course_notes in sorted(
            by_course.items(), key=lambda item: course_names[item[0]]
        ):
            self._add_course_sheet(
                workbook, student, course_id, course_names[course_id],
                course_notes, histories,
                categories, include_terms, data.term_configurations,
            )

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            workbook.save(path)
        except OSError as error:
            raise ValidationError("No s’ha pogut desar l’informe.") from error
        return path

    def _add_course_sheet(
        self, workbook, student, course_id, course_name, notes, histories,
        categories, include_terms: bool, term_configurations,
    ) -> None:
        from openpyxl.styles import Alignment, Font, PatternFill

        sheet = workbook.create_sheet(self._sheet_title(course_name))
        group_by_note_id = self._group_for_notes(notes, histories, student.group_name)
        term_by_note_id = (
            self._term_for_notes(notes, course_id, group_by_note_id, term_configurations)
            if include_terms else None
        )
        groups = list(dict.fromkeys(
            group_by_note_id[note.id] for note in notes if group_by_note_id[note.id]
        ))
        last_column = len(categories) + (2 if include_terms else 1)
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_column)
        title = sheet.cell(1, 1)
        self._set_text(title, f"{student.filing_name} — {', '.join(groups) or 'Sense grup'}")
        title.font = Font(bold=True, size=14, color="FFFFFF")
        title.fill = PatternFill("solid", fgColor="173A5E")
        title.alignment = Alignment(horizontal="center", vertical="center")
        sheet.row_dimensions[1].height = 25

        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_column)
        export_date = sheet.cell(2, 1)
        self._set_text(
            export_date, f"Data d’exportació: {date.today().strftime('%d/%m/%Y')}"
        )
        export_date.font = Font(italic=True, color="64748B")
        export_date.alignment = Alignment(horizontal="right")

        headers = (["Trimestre"] if include_terms else []) + ["Grup"] + [
            category.name for category in categories
        ]
        for column, header in enumerate(headers, 1):
            cell = sheet.cell(3, column)
            self._set_text(cell, header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="2B73B7")
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )

        term_column = 1 if include_terms else None
        group_column = 2 if include_terms else 1
        category_columns = {
            category.id: index
            for index, category in enumerate(categories, group_column + 1)
        }

        last_row = self._write_segments(
            sheet, notes, group_by_note_id, term_by_note_id,
            term_column, group_column, category_columns,
        )
        self._merge_consecutive_values(sheet, group_column, 4, last_row)
        if include_terms:
            self._merge_consecutive_values(sheet, term_column, 4, last_row)
        self._format_sheet(sheet, last_column)

    def _write_segments(
        self, sheet, notes, group_by_note_id, term_by_note_id,
        term_column, group_column, category_columns,
    ) -> int:
        """Escriu cada tram de grup/trimestre constant i en retorna l'última fila.

        Dins d'un tram, cada categoria s'omple des de la primera fila del
        tram amb les seves pròpies notes, ordenades per data i sense deixar
        buits inicials: el nombre de notes d'una categoria dins del tram no
        té per què coincidir amb el d'una altra.
        """
        from openpyxl.styles import Alignment

        row = 4
        for segment_group, segment_term, segment_notes in self._segment_notes(
            notes, group_by_note_id, term_by_note_id
        ):
            notes_by_category = defaultdict(list)
            for note in segment_notes:
                notes_by_category[note.category_id].append(note)
            segment_length = max((len(entries) for entries in notes_by_category.values()), default=1)

            for offset in range(segment_length):
                current_row = row + offset
                group_cell = sheet.cell(current_row, group_column)
                self._set_text(group_cell, segment_group)
                group_cell.alignment = Alignment(vertical="top")
                if term_column is not None:
                    term_cell = sheet.cell(current_row, term_column)
                    self._set_text(term_cell, segment_term)
                    term_cell.alignment = Alignment(vertical="top")

            for category_id, category_notes in notes_by_category.items():
                column = category_columns.get(category_id)
                if column is None:
                    continue
                for offset, note in enumerate(category_notes):
                    display_date = date.fromisoformat(note.date).strftime("%d/%m/%Y")
                    cell = sheet.cell(row + offset, column)
                    self._set_text(cell, f"{display_date} - {note.content}")
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
            row += segment_length
        return row - 1

    @staticmethod
    def _segment_notes(notes, group_by_note_id, term_by_note_id):
        """Parteix les notes (ja ordenades per data) en trams de grup/trimestre constant.

        Cada canvi de grup o de trimestre comença un tram nou, de manera que
        dins d'un mateix tram el valor de totes dues columnes és constant i
        vàlid per a qualsevol nota que s'hi col·loqui, independentment de la
        categoria a què pertanyi.
        """
        segments = []
        current_key = None
        for note in notes:
            term = term_by_note_id[note.id] if term_by_note_id is not None else ""
            key = (group_by_note_id[note.id], term)
            if key != current_key:
                segments.append((key[0], key[1], []))
                current_key = key
            segments[-1][2].append(note)
        return segments

    @staticmethod
    def _term_for_notes(notes, course_id, group_by_note_id, term_configurations) -> dict[int, str]:
        """Calcula el trimestre de cada nota a partir de la seva data i grup."""
        result: dict[int, str] = {}
        for note in notes:
            group = group_by_note_id[note.id]
            configuration = term_configurations.get((course_id, group)) if group else None
            if configuration is None:
                term = ""
            elif note.date < configuration.second_term_start:
                term = "1r"
            elif note.date < configuration.third_term_start:
                term = "2n"
            else:
                term = "3r"
            result[note.id] = term
        return result

    @staticmethod
    def _course_names(by_course, names) -> dict[int, str]:
        missing = set(by_course) - names.keys()
        if missing:
            raise ValidationError("Una nota fa referència a un curs acadèmic inexistent.")
        return names

    @staticmethod
    def _group_for_notes(notes, histories, fallback: str) -> dict[int, str]:
        """Resol el grup de cada nota en un únic recorregut ordenat.

        Aprofita que `notes` ja arriba ordenat per data i que
        `StudentGroupHistoryDAO.get_by_students` retorna l'historial ordenat
        per `start_date`, evitant tornar a recórrer tot l'historial per cada
        nota (O(N·H) -> O(N + H) en el cas habitual de trams no superposats).
        """
        ordered_histories = sorted(
            histories, key=lambda history: (history.start_date, history.id)
        )
        active: list = []
        next_index = 0
        result: dict[int, str] = {}
        for note in notes:
            while (
                next_index < len(ordered_histories)
                and ordered_histories[next_index].start_date <= note.date
            ):
                active.append(ordered_histories[next_index])
                next_index += 1
            active = [
                history for history in active
                if history.end_date is None or note.date <= history.end_date
            ]
            result[note.id] = (
                max(active, key=lambda history: (history.start_date, history.id)).group_name
                if active else fallback
            )
        return result

    @staticmethod
    def _sheet_title(course_name: str) -> str:
        invalid = set('[]:*?/\\')
        title = "".join("-" if character in invalid else character for character in course_name)
        return title[:31] or "Curs"

    @classmethod
    def _safe_text(cls, value) -> str:
        """Prepara text Unicode vàlid per a una cel·la OOXML d'Excel."""
        from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

        text = unicodedata.normalize("NFC", "" if value is None else str(value))
        text = ILLEGAL_CHARACTERS_RE.sub("", text)
        return text[:cls.EXCEL_CELL_LIMIT]

    @classmethod
    def _set_text(cls, cell, value) -> None:
        """Força una cel·la a text, inclosos valors que comencen per ``=``."""
        cell.value = cls._safe_text(value)
        cell.data_type = "s"

    @staticmethod
    def _merge_consecutive_values(sheet, column: int, first_row: int, last_row: int) -> None:
        from openpyxl.styles import Alignment

        start = first_row
        while start <= last_row:
            value = sheet.cell(start, column).value
            end = start
            while end + 1 <= last_row and sheet.cell(end + 1, column).value == value:
                end += 1
            if value and end > start:
                sheet.merge_cells(start_row=start, start_column=column,
                                  end_row=end, end_column=column)
                sheet.cell(start, column).alignment = Alignment(
                    horizontal="center", vertical="center"
                )
            start = end + 1

    @staticmethod
    def _format_sheet(sheet, last_column: int) -> None:
        from openpyxl.utils import get_column_letter

        sheet.freeze_panes = "A4"
        sheet.auto_filter.ref = f"A3:{get_column_letter(last_column)}{sheet.max_row}"
        for column in range(1, last_column + 1):
            letter = get_column_letter(column)
            sheet.column_dimensions[letter].width = 14 if column <= 2 else 34
