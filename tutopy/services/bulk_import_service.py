from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from tutopy.models.bulk_import import (
    CategoryImportRow, ImportAction, ImportDecision, ImportIssue, ImportPreview,
    ImportResult, StudentConflict, StudentImportRow,
)
from tutopy.models.messaging import CategoryNew, Student, StudentNew
from tutopy.services.category_service import CategoryService
from tutopy.services.exceptions import ValidationError
from tutopy.services.student_service import StudentService


class BulkImportService:
    STUDENTS_SHEET = "Alumnes"
    CATEGORIES_SHEET = "Categories"
    STUDENT_HEADERS = ("Nom", "Cognoms", "Grup")
    CATEGORY_HEADERS = ("Nom",)

    def __init__(self, students: StudentService, categories: CategoryService,
                 transaction_factory, similarity_threshold: float = 0.86):
        self.students = students
        self.categories = categories
        self.transaction_factory = transaction_factory
        self.similarity_threshold = similarity_threshold

    def create_template(self, destination: str | Path) -> Path:
        path = Path(destination)
        if path.suffix.lower() != ".xlsx":
            path = path.with_suffix(".xlsx")
        workbook = Workbook()
        instructions = workbook.active
        instructions.title = "Instruccions"
        instructions.append(["Plantilla d’importació de Tutopy"])
        instructions.append(["Omple els fulls Alumnes i Categories. No canviïs les capçaleres."])
        instructions.append(["El nom i els cognoms són obligatoris; el grup és opcional."])
        students = workbook.create_sheet(self.STUDENTS_SHEET)
        students.append(self.STUDENT_HEADERS)
        categories = workbook.create_sheet(self.CATEGORIES_SHEET)
        categories.append(self.CATEGORY_HEADERS)
        for sheet in (students, categories):
            for cell in sheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="2B73B7")
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
        students.column_dimensions["A"].width = 22
        students.column_dimensions["B"].width = 32
        students.column_dimensions["C"].width = 18
        categories.column_dimensions["A"].width = 30
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(path)
        return path

    def analyze(self, source: str | Path) -> ImportPreview:
        path = Path(source)
        if not path.is_file():
            raise ValidationError("El full de càlcul seleccionat no existeix.")
        try:
            workbook = load_workbook(path, read_only=True, data_only=False)
        except Exception as error:
            raise ValidationError("No s’ha pogut obrir el fitxer com a full XLSX.") from error

        issues: list[ImportIssue] = []
        student_rows: list[StudentImportRow] = []
        category_rows: list[CategoryImportRow] = []
        self._read_students(workbook, student_rows, issues)
        self._read_categories(workbook, category_rows, issues)
        existing = self.students.get_all()
        conflicts = []
        for row in student_rows:
            matches = tuple(student for student in existing if self._similar(row, student))
            if matches:
                conflicts.append(StudentConflict(row, matches))
        return ImportPreview(tuple(student_rows), tuple(category_rows),
                             tuple(conflicts), tuple(issues))

    def execute(self, preview: ImportPreview,
                decisions: tuple[ImportDecision, ...] = ()) -> ImportResult:
        if preview.issues:
            raise ValidationError("\n".join(str(issue) for issue in preview.issues))
        decision_by_row = {decision.row: decision for decision in decisions}
        conflict_rows = {conflict.row.row: conflict for conflict in preview.conflicts}
        missing = sorted(set(conflict_rows) - set(decision_by_row))
        if missing:
            raise ValidationError(
                "Falten decisions per a les files d’alumnes: "
                + ", ".join(map(str, missing))
            )
        created = updated = skipped = categories_created = categories_reused = 0
        with self.transaction_factory():
            for row in preview.students:
                decision = decision_by_row.get(
                    row.row, ImportDecision(row.row, ImportAction.CREATE)
                )
                try:
                    if decision.action == ImportAction.SKIP:
                        skipped += 1
                    elif decision.action == ImportAction.UPDATE:
                        target = self.students.get_by_id(decision.student_id or 0)
                        allowed = conflict_rows.get(row.row)
                        if target is None or allowed is None or target.id not in {
                            item.id for item in allowed.matches
                        }:
                            raise ValidationError("l’alumne seleccionat no és una coincidència vàlida")
                        self.students.update(Student(target.id, target.uuid, row.name,
                                                     row.surnames, row.group_name))
                        updated += 1
                    else:
                        self.students.create(StudentNew(row.name, row.surnames, row.group_name))
                        created += 1
                except Exception as error:
                    raise ValidationError(
                        f"{self.STUDENTS_SHEET} — fila {row.row}: {error}"
                    ) from error

            existing_categories = {
                self._category_key(category.name): category for category in self.categories.get_all()
            }
            for row in preview.categories:
                key = self._category_key(row.name)
                if key in existing_categories:
                    categories_reused += 1
                    continue
                try:
                    category = self.categories.create(CategoryNew(row.name))
                    existing_categories[key] = category
                    categories_created += 1
                except Exception as error:
                    raise ValidationError(
                        f"{self.CATEGORIES_SHEET} — fila {row.row}: {error}"
                    ) from error
        return ImportResult(created, updated, skipped, categories_created, categories_reused)

    def _read_students(self, workbook, output, issues) -> None:
        sheet = self._sheet(workbook, self.STUDENTS_SHEET, issues)
        if sheet is None or not self._headers(sheet, self.STUDENT_HEADERS, issues):
            return
        for number, values in enumerate(sheet.iter_rows(min_row=2, max_col=3, values_only=True), 2):
            if all(value is None or str(value).strip() == "" for value in values):
                continue
            cells = [self._cell(value, self.STUDENTS_SHEET, number, issues) for value in values]
            name, surnames, group = cells
            if not name:
                issues.append(ImportIssue(self.STUDENTS_SHEET, number, "el nom és obligatori"))
            if not surnames:
                issues.append(ImportIssue(self.STUDENTS_SHEET, number, "els cognoms són obligatoris"))
            if name and surnames:
                output.append(StudentImportRow(number, name, surnames, group))

    def _read_categories(self, workbook, output, issues) -> None:
        sheet = self._sheet(workbook, self.CATEGORIES_SHEET, issues)
        if sheet is None or not self._headers(sheet, self.CATEGORY_HEADERS, issues):
            return
        for number, (value,) in enumerate(sheet.iter_rows(min_row=2, max_col=1, values_only=True), 2):
            if value is None or str(value).strip() == "":
                continue
            name = self._cell(value, self.CATEGORIES_SHEET, number, issues)
            if name:
                output.append(CategoryImportRow(number, name))

    def _sheet(self, workbook, name, issues):
        if name not in workbook.sheetnames:
            issues.append(ImportIssue(name, 1, f"falta el full «{name}»"))
            return None
        return workbook[name]

    def _headers(self, sheet, expected, issues) -> bool:
        actual = tuple(cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1,
                                                                    max_col=len(expected))))
        if actual != expected:
            issues.append(ImportIssue(sheet.title, 1,
                                      "les capçaleres han de ser: " + ", ".join(expected)))
            return False
        return True

    @staticmethod
    def _cell(value, sheet, row, issues) -> str:
        if value is None:
            return ""
        if isinstance(value, str) and value.startswith("="):
            issues.append(ImportIssue(sheet, row, "no s’admeten fórmules"))
            return ""
        if not isinstance(value, (str, int, float)) or isinstance(value, bool):
            issues.append(ImportIssue(sheet, row, "el valor ha de ser text"))
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())

    @staticmethod
    def _category_key(value: str) -> str:
        """Igualtat de categoria: majúscules i espais, però no accents ni grafies."""
        return " ".join(value.casefold().split())

    def _similar(self, row: StudentImportRow, student: Student) -> bool:
        incoming = self._normalize(row.full_name)
        current = self._normalize(student.full_name)
        return incoming == current or SequenceMatcher(None, incoming, current).ratio() >= self.similarity_threshold
