from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import Note, NoteNew, NoteRecord
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.validation_service import ValidationService
from tutopy.services.utils import AcademicCourseDeterminator


class NoteService:
    def __init__(self, note_dao: NoteDAO, academic_course_dao: AcademicCourseDAO,
        category_dao: CategoryDAO, student_dao: StudentDAO, transaction_factory):
        self.note_dao = note_dao
        self.academic_course_dao = academic_course_dao
        self.category_dao = category_dao
        self.student_dao = student_dao
        self.transaction_factory = transaction_factory
        self.validation_service = ValidationService(category_dao)

    def create_note(self, note_data: NoteNew) -> Note:
        """Valida i crea una nota de seguiment."""
        with self.transaction_factory():
            prepared = self._prepare(note_data)
            return self.note_dao.create(prepared)

    def create(self, note_data: NoteNew) -> Note:
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
        return self.get_notes_by_student(student_id)

    def get_all(self) -> list[Note]:
        return self.note_dao.get_all()

    def get_by_id(self, note_id: int) -> Note:
        self.validation_service.positive_id(note_id)
        note = self.note_dao.get_by_id(note_id)
        if note is None:
            raise EntityNotFoundError(f"La nota amb ID {note_id} no existeix.")
        return note

    def update(self, note: Note) -> Note:
        with self.transaction_factory():
            self.get_by_id(note.id)
            prepared = self._prepare(NoteNew(
                student_id=note.student_id,
                category_id=note.category_id,
                date=note.date,
                course_id=note.course_id,
                content=note.content,
            ))
            note.student_id = prepared.student_id
            note.category_id = prepared.category_id
            note.date = prepared.date
            note.course_id = prepared.course_id
            note.content = prepared.content
            self.note_dao.update(note)
            return note

    def delete(self, note_id: int) -> None:
        self.get_by_id(note_id)
        self.note_dao.delete(note_id)

    def get_records(self, filters: dict = None) -> list[NoteRecord]:
        """Retorna notes per a la taula de la UI amb filtres combinats amb AND."""
        return self.note_dao.get_records(self._validate_filters(filters or {}))

    def _prepare(self, note_data: NoteNew) -> NoteNew:
        prepared = NoteNew(
            student_id=note_data.student_id,
            category_id=note_data.category_id,
            date=note_data.date,
            course_id=note_data.course_id,
            content=note_data.content,
        )
        self.validation_service.validate_note(prepared)
        self._require_student(prepared.student_id)
        course_id = prepared.course_id
        if course_id == 0:
            course_id = self._resolve_academic_course(prepared.date)
        elif self.academic_course_dao.get_by_id(course_id) is None:
            raise EntityNotFoundError(
                f"El curs acadèmic amb ID {course_id} no existeix."
            )
        return NoteNew(
            student_id=prepared.student_id,
            category_id=prepared.category_id,
            date=prepared.date,
            course_id=course_id,
            content=prepared.content,
        )

    def _require_student(self, student_id: int):
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student

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
