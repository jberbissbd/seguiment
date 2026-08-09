import uuid
import pytest
from tutopy.models.messaging import NoteNew, CategoryNew, AcademicCourseNew, StudentNew, Note
from tutopy.services.note_service import NoteService


class TestNoteService:
    """Tests per a NoteService."""

    def test_create_note_with_existing_course(self, note_dao, academic_course_dao, category_dao, db):
        """Testa la creació d'una nota amb un curs acadèmic existent."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao)
        
        # Crear nota amb course_id existent
        note_data = NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-01-15",
            course_id=curs.id,
            content="Nota de prova"
        )
        
        # Executar
        created_note = service.create_note(note_data)
        
        # Verificar
        assert created_note.id is not None
        assert created_note.student_id == alumne.id
        assert created_note.category_id == categoria.id
        assert created_note.course_id == curs.id
        assert created_note.content == "Nota de prova"
        assert created_note.date == "2026-01-15"

    def test_create_note_resolves_course_from_september_date(self, note_dao, academic_course_dao, category_dao, db):
        """Testa que una nota amb course_id=0 i data de setembre resol el curs automàticament."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Conducta"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Anna", "Martínez", "3r B"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao)
        
        # Crear nota amb course_id=0 (per resoldre automàticament)
        note_data = NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-09-15",
            course_id=0,
            content="Nota amb curs resolt"
        )
        
        # Executar
        created_note = service.create_note(note_data)
        
        # Verificar que s'ha resolt el curs 2026-2027
        assert created_note.course_id is not None
        curs = db.academic_courses.get_by_id(created_note.course_id)
        assert curs.course == "2026-2027"

    def test_create_note_resolves_course_from_january_date(self, note_dao, academic_course_dao, category_dao, db):
        """Testa que una nota amb course_id=0 i data de gener resol el curs anterior."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Incidència"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Pere", "López", "2n A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao)
        
        # Crear nota amb course_id=0 i data de gener
        note_data = NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-01-20",
            course_id=0,
            content="Nota de gener"
        )
        
        # Executar
        created_note = service.create_note(note_data)
        
        # Verificar que s'ha resolt el curs 2025-2026
        assert created_note.course_id is not None
        curs = db.academic_courses.get_by_id(created_note.course_id)
        assert curs.course == "2025-2026"

    def test_get_notes_by_student(self, note_dao, academic_course_dao, category_dao, db):
        """Testa l'obtenció de notes per un alumne específic."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear algunes notes per aquest alumne
        note1 = db.notes.create(NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-01-01",
            course_id=curs.id,
            content="Nota 1"
        ))
        note2 = db.notes.create(NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-01-02",
            course_id=curs.id,
            content="Nota 2"
        ))
        
        # Crear una nota per un altre alumne (per verificar que no es retorni)
        uuid_altre = str(uuid.uuid4())
        altre = db.students.create(StudentNew("Anna", "Martínez", "4t A"))
        db.notes.create(NoteNew(
            student_id=altre.id,
            category_id=categoria.id,
            date="2026-01-03",
            course_id=curs.id,
            content="Nota d'un altre"
        ))
        
        # Crear el servei i obtenir notes
        service = NoteService(note_dao, academic_course_dao, category_dao)
        notes = service.get_notes_by_student(alumne.id)
        
        # Verificar
        assert len(notes) == 2
        assert all(n.student_id == alumne.id for n in notes)
        # Verificar que conté les dates esperades (ordre pot variar)
        dates = [n.date for n in notes]
        assert "2026-01-01" in dates
        assert "2026-01-02" in dates

    def test_get_notes_by_student_empty(self, note_dao, academic_course_dao, category_dao, db):
        """Testa l'obtenció de notes per un alumne sense notes."""
        # Crear un alumne sense notes
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Maria", "Sánchez", "1r A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao)
        
        # Obtenir notes
        notes = service.get_notes_by_student(alumne.id)
        
        # Verificar
        assert notes == []
