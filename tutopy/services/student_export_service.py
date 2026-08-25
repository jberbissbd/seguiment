"""Exportació d'informes i documents d'alumnes a carpetes locals, individual o en lot."""

from pathlib import Path
import re
from datetime import date
from dataclasses import dataclass
from typing import Any, Callable

from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.report_file_service import ReportFileService
from tutopy.services.validation_service import ValidationService
from tutopy.models.reporting import BatchExportFailure, BatchExportResult


@dataclass(frozen=True, slots=True)
class StudentExportPreparation:
    """Snapshot sense accés posterior a SQLite per exportar en un treballador."""

    student_ids: tuple[int, ...]
    destination: Path
    report_format: str
    include_terms: bool
    include_documents: bool
    report_data: Any
    document_data: Any


class StudentExportService:
    """Exporta l'informe i els documents d'un alumne en una carpeta ordenada."""

    def __init__(self, students: StudentDAO, documents: DocumentService,
                 courses: AcademicCourseDAO, report_files: ReportFileService):
        """Injecta els DAOs i serveis necessaris per exportar alumnes."""
        self.students = students
        self.documents = documents
        self.courses = courses
        self.report_files = report_files
        self.validation = ValidationService()

    def export_student(self, student_id: int, destination: str | Path,
                       report_format: str, include_terms: bool = False,
                       include_documents: bool = True,
                       folder_name: str | None = None) -> Path:
        """Exporta l'informe i, opcionalment, els documents d'un sol alumne.

        Args:
            student_id: ID de l'alumne a exportar.
            destination: Carpeta on crear la carpeta d'exportació.
            report_format: Format de l'informe (ex: "pdf", "docx").
            include_terms: Si cal incloure els trimestres a l'informe.
            include_documents: Si cal copiar-hi també els documents de l'alumne.
            folder_name: Nom de la subcarpeta a crear. Si no s'especifica,
                es deriva del nom de l'alumne.

        Returns:
            La carpeta creada amb l'informe (i documents, si s'escau).
        """
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
                        include_documents: bool = False,
                        progress_callback: Callable[[int, int], None] | None = None,
                        cancel_requested: Callable[[], bool] | None = None,
                        ) -> BatchExportResult:
        """Prepara i exporta en lot l'informe (i documents) de diversos alumnes.

        Args:
            student_ids: IDs dels alumnes a exportar.
            destination: Carpeta on crear la carpeta del lot.
            report_format: Format de l'informe (ex: "pdf", "docx").
            include_terms: Si cal incloure els trimestres a l'informe.
            include_documents: Si cal copiar-hi també els documents de cada alumne.
            progress_callback: Rebut amb (processats, total) després de cada alumne.
            cancel_requested: Consultat entre alumnes per aturar el lot.

        Returns:
            El resultat del lot, amb els alumnes processats i les fallades.
        """
        preparation = self.prepare_students_export(
            student_ids, destination, report_format, include_terms, include_documents
        )
        return self.export_prepared(
            preparation, progress_callback=progress_callback,
            cancel_requested=cancel_requested,
        )

    def prepare_students_export(
        self, student_ids: list[int], destination: str | Path,
        report_format: str, include_terms: bool = False,
        include_documents: bool = False,
    ) -> StudentExportPreparation:
        """Valida i carrega al fil actual totes les dades requerides pel lot."""
        base = self._validate_batch_request(student_ids, destination, report_format)
        report_data = self.report_files.prepare_students(
            student_ids, report_format, include_terms
        )
        document_data = (
            self._prepare_documents(student_ids) if include_documents else None
        )
        return StudentExportPreparation(
            tuple(student_ids), base, report_format, include_terms,
            include_documents, report_data, document_data,
        )

    def export_prepared(
        self, preparation: StudentExportPreparation,
        progress_callback: Callable[[int, int], None] | None = None,
        cancel_requested: Callable[[], bool] | None = None,
    ) -> BatchExportResult:
        """Genera un lot preparat sense efectuar cap lectura de SQLite."""
        batch_root = self._create_batch_root(preparation.destination)
        failures = []
        used_folders = {}
        processed = 0
        total = len(preparation.student_ids)
        for student_id in preparation.student_ids:
            if cancel_requested is not None and cancel_requested():
                break
            failure = self._export_batch_entry(
                student_id, batch_root, preparation.report_format,
                preparation.include_terms, preparation.include_documents,
                used_folders, preparation.report_data, preparation.document_data,
            )
            if failure is not None:
                failures.append(failure)
            processed += 1
            if progress_callback is not None:
                progress_callback(processed, total)
        return BatchExportResult(
            str(batch_root), processed - len(failures), tuple(failures),
            cancelled=processed < total,
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
                            used_folders: dict[str, int],
                            report_data, document_data) -> BatchExportFailure | None:
        student = None
        student_root = None
        try:
            student_id = self.validation.positive_id(student_id)
            student = report_data.students.get(student_id)
            if student is None:
                raise EntityNotFoundError("L’alumne seleccionat no existeix.")
            folder_name = self._next_student_folder(student.filing_name, used_folders)
            student_root = batch_root / folder_name
            student_root.mkdir(parents=True, exist_ok=True)
            self.report_files.export_prepared(
                student_id, student_root / f"informe.{report_format}",
                report_format, report_data, include_terms,
            )
            if include_documents:
                self._export_documents(student_id, student_root, document_data)
            return None
        except (ValidationError, EntityNotFoundError, OSError) as error:
            self._recover_documents(
                include_documents, student, student_root, document_data
            )
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
                           student_root: Path | None, document_data=None) -> None:
        if not include_documents or student is None or student_root is None:
            return
        try:
            student_root.mkdir(parents=True, exist_ok=True)
            self._export_documents(student.id, student_root, document_data)
        except (ValidationError, EntityNotFoundError, OSError):
            pass

    def _prepare_documents(self, student_ids: list[int]):
        return (
            {course.id: course for course in self.courses.get_all()},
            self.documents.get_by_students(student_ids),
        )

    def _export_documents(
        self, student_id: int, root: Path, document_data=None
    ) -> None:
        used_names = {}
        if document_data is None:
            courses_by_id = {course.id: course for course in self.courses.get_all()}
            documents = self.documents.get_by_student(student_id)
        else:
            courses_by_id, documents_by_student = document_data
            documents = documents_by_student[student_id]
        for document in documents:
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
            self.documents.export_document(
                document, str(course_dir / f"{stem}{suffix}{extension}")
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
