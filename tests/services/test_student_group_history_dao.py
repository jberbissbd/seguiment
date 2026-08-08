import uuid
import pytest
from tutopy.models.messaging import StudentGroupHistory, StudentGroupHistoryNew, AcademicCourseNew, StudentNew
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO


class TestStudentGroupHistoryDAO:
    """Tests per a StudentGroupHistoryDAO."""

    def test_create(self, db):
        """Testa la creació d'un registre d'històric de grup."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        data = StudentGroupHistoryNew(
            student_id=student.id,
            group_name="4t A",
            academic_course_id=None,
            start_date="2026-01-15",
            end_date=None
        )
        
        created = dao.create(data)
        
        assert created.id is not None
        assert created.student_id == student.id
        assert created.group_name == "4t A"
        assert created.start_date == "2026-01-15"
        assert created.end_date is None
        assert created.academic_course_id is None

    def test_get_by_id(self, db):
        """Testa l'obtenció d'un registre pel seu ID."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        created = dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="3r B",
            start_date="2026-01-01"
        ))
        
        retrieved = dao.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.group_name == "3r B"

    def test_get_by_id_nonexistent(self, db):
        """Testa que get_by_id retorna None per ID inexistent."""
        dao = StudentGroupHistoryDAO(db.conn)
        
        result = dao.get_by_id(99999)
        assert result is None

    def test_get_current(self, db):
        """Testa l'obtenció del grup actual (end_date IS NULL)."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        # Crear un registre amb end_date (antic)
        dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="2n A",
            start_date="2025-09-01",
            end_date="2026-06-30"
        ))
        
        # Crear un registre sense end_date (actual)
        current = dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="3r A",
            start_date="2026-09-01"
        ))
        
        # Obtenir el grup actual
        result = dao.get_current(student.id)
        
        assert result is not None
        assert result.id == current.id
        assert result.group_name == "3r A"
        assert result.end_date is None

    def test_get_current_no_active(self, db):
        """Testa que get_current retorna None si no hi ha cap grup actiu."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        # Crear un registre amb end_date (tots tancats)
        dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="2n A",
            start_date="2025-09-01",
            end_date="2026-06-30"
        ))
        
        # No hi ha cap grup actiu
        result = dao.get_current(student.id)
        assert result is None

    def test_get_by_student(self, db):
        """Testa l'obtenció de tot l'històric d'un alumne."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        # Crear diversos registres per al mateix alumne
        dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="1r A",
            start_date="2024-09-01",
            end_date="2025-06-30"
        ))
        dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="2n A",
            start_date="2025-09-01",
            end_date="2026-06-30"
        ))
        dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="3r A",
            start_date="2026-09-01"
        ))
        
        # Obtenir històric
        history = dao.get_by_student(student.id)
        
        # Verificar
        assert len(history) == 3
        assert history[0].group_name == "1r A"
        assert history[1].group_name == "2n A"
        assert history[2].group_name == "3r A"

    def test_get_by_student_empty(self, db):
        """Testa que get_by_student retorna llista buida si no hi ha registres."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        history = dao.get_by_student(student.id)
        assert history == []

    def test_update(self, db):
        """Testa l'actualització d'un registre."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        created = dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="4t A",
            start_date="2026-01-01"
        ))
        
        # Actualitzar
        created.end_date = "2026-06-30"
        dao.update(created)
        
        # Verificar
        updated = dao.get_by_id(created.id)
        assert updated.end_date == "2026-06-30"

    def test_delete(self, db):
        """Testa l'eliminació d'un registre."""
        student = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        created = dao.create(StudentGroupHistoryNew(
            student_id=student.id,
            group_name="4t A",
            start_date="2026-01-01"
        ))
        
        # Eliminar
        dao.delete(created.id)
        
        # Verificar
        assert dao.get_by_id(created.id) is None

    def test_get_by_course(self, db):
        """Testa l'obtenció de registres per curs acadèmic."""
        student1 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test1",
            surnames="User",
            group_name="1r A"
        ))
        student2 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test2",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        # Crear un curs
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        # Crear registres amb aquest curs
        dao.create(StudentGroupHistoryNew(
            student_id=student1.id,
            group_name="4t A",
            academic_course_id=curs.id,
            start_date="2025-09-01"
        ))
        dao.create(StudentGroupHistoryNew(
            student_id=student2.id,
            group_name="4t B",
            academic_course_id=curs.id,
            start_date="2025-09-01"
        ))
        
        # Obtenir per curs
        results = dao.get_by_course(curs.id)
        
        # Verificar
        assert len(results) == 2
        assert all(r.academic_course_id == curs.id for r in results)

    def test_get_by_course_and_date(self, db):
        """Testa l'obtenció de grups actius en una data concreta."""
        student1 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test1",
            surnames="User",
            group_name="1r A"
        ))
        student2 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Test2",
            surnames="User",
            group_name="1r A"
        ))
        
        dao = StudentGroupHistoryDAO(db.conn)
        
        # Crear un curs
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        # Crear registres amb diferents dates
        dao.create(StudentGroupHistoryNew(
            student_id=student1.id,
            group_name="4t A",
            academic_course_id=curs.id,
            start_date="2025-09-01",
            end_date="2025-12-31"
        ))
        dao.create(StudentGroupHistoryNew(
            student_id=student2.id,
            group_name="4t B",
            academic_course_id=curs.id,
            start_date="2026-01-01"  # Actiu el 2026-01-15
        ))
        
        # Obtenir grups actius el 2026-01-15
        results = dao.get_by_course_and_date(curs.id, "2026-01-15")
        
        # Verificar
        assert len(results) == 1
        assert results[0].group_name == "4t B"
