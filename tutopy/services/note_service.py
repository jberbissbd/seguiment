from tutopy.database.daos.note_dao import NoteDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import Note, NoteNew
from tutopy.services.validation_service import validate_note


class NoteService:
    def __init__(self, note_dao: NoteDAO, academic_course_dao: AcademicCourseDAO):
        self.note_dao = note_dao
        self.academic_course_dao = academic_course_dao

    def create_note(self, note_data: NoteNew):
        validate_note(note_data)
        # Si course_id és 0, resol el curs a partir de la data
        if note_data.course_id == 0:
            note_data.course_id = self._resolve_academic_course(note_data.date)
        return self.note_dao.create(note_data)

    def _resolve_academic_course(self, date_str: str) -> int:
        """Resol el curs acadèmic a partir d'una data (ex: 2026-09-01 → 2026-2027)."""
        from tutopy.services.utils import AcademicCourseDeterminator
        course_str = AcademicCourseDeterminator().curs_academic_singular(date_str)
        course = self.academic_course_dao.get_or_create(course_str)
        return course.id

    def get_notes_by_student(self, student_id: int) -> list[Note]:
        """Obté totes les notes d'un alumne, ordenades per data."""
        return self.note_dao.get_by_student(student_id)

