import uuid
import pytest
from tutopy.models.messaging import NoteNew, CategoryNew, AcademicCourseNew, StudentNew, Note
from tutopy.services.note_service import NoteService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


class TestNoteService:
    """Tests per a NoteService."""

    def test_create_note_with_existing_course(self, note_dao, academic_course_dao, category_dao, student_dao, db):
        """Testa la creació d'una nota amb un curs acadèmic existent."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao, student_dao, db.transaction)
        
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

    def test_create_note_ignora_curs_manual_i_utilitza_el_de_la_data(
        self, note_dao, academic_course_dao, category_dao, student_dao, db
    ):
        category = db.categories.create(CategoryNew("Acadèmic"))
        wrong_course = db.academic_courses.create(AcademicCourseNew("2024-2025"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao, db.transaction
        )

        note = service.create(NoteNew(
            student.id, category.id, "2026-09-15", wrong_course.id, "Seguiment"
        ))

        assert note.course_id != wrong_course.id
        assert db.academic_courses.get_by_id(note.course_id).course == "2026-2027"

    def test_create_note_resolves_course_from_september_date(self, note_dao, academic_course_dao, category_dao, student_dao, db):
        """Testa que una nota amb course_id=0 i data de setembre resol el curs automàticament."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Conducta"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Anna", "Martínez", "3r B"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao, student_dao, db.transaction)
        
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

    def test_create_note_resolves_course_from_january_date(self, note_dao, academic_course_dao, category_dao, student_dao, db):
        """Testa que una nota amb course_id=0 i data de gener resol el curs anterior."""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Incidència"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Pere", "López", "2n A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao, student_dao, db.transaction)
        
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

    def test_get_notes_by_student(self, note_dao, academic_course_dao, category_dao, student_dao, db):
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
        service = NoteService(note_dao, academic_course_dao, category_dao, student_dao, db.transaction)
        notes = service.get_notes_by_student(alumne.id)
        
        # Verificar
        assert len(notes) == 2
        assert all(n.student_id == alumne.id for n in notes)
        # Verificar que conté les dates esperades (ordre pot variar)
        dates = [n.date for n in notes]
        assert "2026-01-01" in dates
        assert "2026-01-02" in dates

    def test_get_notes_by_student_empty(self, note_dao, academic_course_dao, category_dao, student_dao, db):
        """Testa l'obtenció de notes per un alumne sense notes."""
        # Crear un alumne sense notes
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Maria", "Sánchez", "1r A"))
        
        # Crear el servei
        service = NoteService(note_dao, academic_course_dao, category_dao, student_dao, db.transaction)
        
        # Obtenir notes
        notes = service.get_notes_by_student(alumne.id)

        # Verificar
        assert notes == []

    def test_crud_complet(self, note_dao, academic_course_dao, category_dao,
        student_dao, db):
        category = db.categories.create(CategoryNew("Acadèmic"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao, db.transaction
        )
        created = service.create(NoteNew(
            student.id, category.id, "2026-01-15", 0, "  Nota inicial  "
        ))

        assert created.content == "Nota inicial"
        assert service.get_by_id(created.id) == created
        assert service.get_all() == [created]

        created.date = "2026-09-01"
        created.course_id = 0
        created.content = "Actualitzada"
        updated = service.update(created)
        assert db.academic_courses.get_by_id(updated.course_id).course == "2026-2027"

        service.delete(created.id)
        with pytest.raises(EntityNotFoundError):
            service.get_by_id(created.id)

    def test_rebutja_alumne_inexistent(self, note_dao, academic_course_dao,
        category_dao, student_dao, db):
        category = db.categories.create(CategoryNew("Acadèmic"))
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao, db.transaction
        )

        note = NoteNew(999, category.id, "2026-01-15", 0, "Nota")
        with pytest.raises(EntityNotFoundError, match="alumne"):
            service.create(note)

    def test_filtres_combinables(self, note_dao, academic_course_dao,
        category_dao, student_dao, db):
        academic = db.categories.create(CategoryNew("Acadèmic"))
        behaviour = db.categories.create(CategoryNew("Conducta"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        other = db.students.create(StudentNew("Anna", "Serra", "4t B"))
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao, db.transaction
        )
        service.create(NoteNew(
            student.id, academic.id, "2026-01-10", 0, "Progrés notable"
        ))
        service.create(NoteNew(
            student.id, behaviour.id, "2026-02-10", 0, "Incidència"
        ))
        service.create(NoteNew(
            other.id, academic.id, "2026-01-20", 0, "Progrés"
        ))

        records = service.get_records({
            "student_id": student.id,
            "category_id": academic.id,
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "content": "NOTABLE",
        })

        assert len(records) == 1
        assert records[0].student_id == student.id
        assert records[0].category_id == academic.id

    def test_filtre_rebutja_interval_invertit(self, note_dao,
        academic_course_dao, category_dao, student_dao, db):
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao, db.transaction
        )
        filters = {"date_from": "2026-02-01", "date_to": "2026-01-01"}
        with pytest.raises(ValidationError, match="data inicial"):
            service.get_records(filters)

    def test_create_es_atomic_si_falla_despres_de_crear_el_curs(self, note_dao,
        academic_course_dao, category_dao, student_dao, db, monkeypatch):
        category = db.categories.create(CategoryNew("Acadèmic"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        service = NoteService(
            note_dao, academic_course_dao, category_dao, student_dao,
            db.transaction,
        )

        def fail_create(_data):
            raise RuntimeError("fallada simulada")

        monkeypatch.setattr(note_dao, "create", fail_create)
        note = NoteNew(student.id, category.id, "2026-09-01", 0, "Nota")
        with pytest.raises(RuntimeError, match="fallada simulada"):
            service.create(note)

        assert academic_course_dao.get_by_course("2026-2027") is None
        assert note_dao.get_all() == []
