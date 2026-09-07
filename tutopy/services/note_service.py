"""Servei de gestió de les notes de seguiment dels alumnes."""

import dataclasses
from typing import cast

from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.models.messaging import (
    Note, NoteNew, NoteRecord, Student, StudentGroupHistoryNew,
)
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services._student_requirement import RequiresStudentMixin
from tutopy.services.validation_service import ValidationService
from tutopy.services.utils import AcademicCourseDeterminator


class NoteService(RequiresStudentMixin):
    """Servei per gestionar notes de seguiment, amb registre automàtic de grup."""

    def __init__(self, note_dao: NoteDAO, academic_course_dao: AcademicCourseDAO,
        category_dao: CategoryDAO, student_dao: StudentDAO, transaction_factory,
        group_history_dao: StudentGroupHistoryDAO = None):
        """Rep els DAOs de domini i, opcionalment, l'historial de grups.

        Si `group_history_dao` no s'indica, no es registra automàticament
        l'historial de grup en crear o actualitzar notes.
        """
        self.note_dao = note_dao
        self.academic_course_dao = academic_course_dao
        self.category_dao = category_dao
        self.student_dao = student_dao
        self.transaction_factory = transaction_factory
        self.group_history_dao = group_history_dao
        self.validation_service = ValidationService(category_dao)

    def create_note(self, note_data: NoteNew) -> Note:
        """Valida i crea una nota de seguiment."""
        with self.transaction_factory():
            prepared, student = self._prepare(note_data)
            self._ensure_group_history(prepared, student)
            return self.note_dao.create(prepared)

    def create(self, note_data: NoteNew) -> Note:
        """Àlies de `create_note`."""
        return self.create_note(note_data)

    def _resolve_academic_course(self, date_str: str) -> int:
        """Resol el curs acadèmic a partir d'una data (ex: 2026-09-01 → 2026-2027)."""
        course_str = AcademicCourseDeterminator().curs_academic_singular(date_str)
        course = self.academic_course_dao.get_or_create(course_str)
        return course.id

    def get_notes_by_student(self, student_id: int) -> list[Note]:
        """Obté totes les notes d'un alumne, ordenades per data."""
        self._require_student(student_id)
        return self.note_dao.get_by_student(student_id)

    def get_by_student(self, student_id: int) -> list[Note]:
        """Àlies de `get_notes_by_student`."""
        return self.get_notes_by_student(student_id)

    def get_all(self) -> list[Note]:
        """Retorna totes les notes de tots els alumnes."""
        return self.note_dao.get_all()

    def get_by_id(self, note_id: int) -> Note:
        """Retorna una nota pel seu ID."""
        self.validation_service.positive_id(note_id)
        note = self.note_dao.get_by_id(note_id)
        if note is None:
            raise EntityNotFoundError(f"La nota amb ID {note_id} no existeix.")
        return note

    def update(self, note: Note) -> Note:
        """Valida i actualitza una nota existent, actualitzant l'historial de grup."""
        with self.transaction_factory():
            existing = self.get_by_id(note.id)
            prepared, student = self._prepare(NoteNew(
                student_id=note.student_id,
                category_id=note.category_id,
                date=note.date,
                course_id=note.course_id,
                content=note.content,
            ))
            self._ensure_group_history(prepared, student)
            updated = cast(Note, dataclasses.replace(
                existing,
                student_id=prepared.student_id,
                category_id=prepared.category_id,
                date=prepared.date,
                course_id=prepared.course_id,
                content=prepared.content,
            ))
            self.note_dao.update(updated)
            return updated

    def delete(self, note_id: int) -> None:
        """Elimina una nota pel seu ID."""
        self.get_by_id(note_id)
        self.note_dao.delete(note_id)

    def get_records(self, filters: dict = None) -> list[NoteRecord]:
        """Retorna notes per a la taula de la UI amb filtres combinats amb AND."""
        return self.note_dao.get_records(self._validate_filters(filters or {}))

    def _prepare(self, note_data: NoteNew) -> tuple[NoteNew, Student]:
        prepared = NoteNew(
            student_id=note_data.student_id,
            category_id=note_data.category_id,
            date=note_data.date,
            course_id=note_data.course_id,
            content=note_data.content,
        )
        prepared = self.validation_service.validate_note(prepared)
        student = self._require_student(prepared.student_id)
        # El curs és una dada derivada de la data, no una elecció manual.
        course_id = self._resolve_academic_course(prepared.date)
        return NoteNew(
            student_id=prepared.student_id,
            category_id=prepared.category_id,
            date=prepared.date,
            course_id=course_id,
            content=prepared.content,
        ), student

    def _ensure_group_history(self, note: NoteNew, student: Student) -> None:
        """Registra el curs/grup de la data de la nota si encara no consta."""
        if self.group_history_dao is None:
            return
        histories = self.group_history_dao.get_by_student(note.student_id)
        if any(
            history.academic_course_id == note.course_id
            and history.group_name == student.group_name
            for history in histories
        ):
            return
        current = self.group_history_dao.get_current(note.student_id)
        first_entry_in_course = not histories or (
            current is not None
            and current.group_name == student.group_name
            and current.academic_course_id != note.course_id
        )
        start_date = self._course_start(note.course_id) if first_entry_in_course else note.date
        if current and start_date >= current.start_date:
            self.group_history_dao.update(
                dataclasses.replace(current, end_date=start_date)
            )
            group_name = student.group_name
            end_date = None
        else:
            following = next(
                (history for history in histories if history.start_date > start_date), None
            )
            group_name = student.group_name
            end_date = following.start_date if following else None
        self.group_history_dao.create(StudentGroupHistoryNew(
            student_id=note.student_id,
            group_name=group_name,
            academic_course_id=note.course_id,
            start_date=start_date,
            end_date=end_date,
        ))

    def _course_start(self, course_id: int) -> str:
        course = self.academic_course_dao.get_by_id(course_id)
        if course is None:
            raise EntityNotFoundError("El curs acadèmic de la nota no existeix.")
        first_year = course.course.split("-", 1)[0]
        return f"{first_year}-09-01"

    def _validate_filters(self, filters: dict) -> dict:
        allowed = {"student_id", "category_id", "course_id", "date_from", "date_to", "content"}
        unknown = set(filters) - allowed
        if unknown:
            raise ValidationError(f"Filtres desconeguts: {', '.join(sorted(unknown))}")
        result = {}
        for key in ("student_id", "category_id", "course_id"):
            if filters.get(key) is not None:
                result[key] = self.validation_service.positive_id(filters[key])
        for key in ("date_from", "date_to"):
            if filters.get(key):
                result[key] = self.validation_service.iso_date(filters[key])
        if result.get("date_from") and result.get("date_to"):
            if result["date_from"] > result["date_to"]:
                raise ValidationError("La data inicial no pot ser posterior a la data final.")
        if filters.get("content") is not None:
            content = self.validation_service.optional_text(filters["content"])
            if content:
                result["content"] = content
        return result
