import pytest
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew
from tutopy.services.exceptions import EntityInUseError, ValidationError


class TestAcademicCourseService:
    """Tests per a AcademicCourseService amb base de dades real."""

    def test_get_all_empty(self, academic_course_dao, db):
        """Testa get_all quan no hi ha cursos."""
        service = AcademicCourseService(academic_course_dao)
        result = service.get_all()
        assert result == []

    def test_get_all_with_courses(self, academic_course_dao, db):
        """Testa get_all amb cursos existents."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear cursos directament a la BD
        db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        db.academic_courses.create(AcademicCourseNew(course="2025-2026"))
        
        result = service.get_all()
        
        assert len(result) == 2
        assert {c.course for c in result} == {"2024-2025", "2025-2026"}

    def test_get_by_id(self, academic_course_dao, db):
        """Testa get_by_id amb un curs existent."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear curs
        created = db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        
        result = service.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.course == "2024-2025"

    def test_get_by_id_not_found(self, academic_course_dao, db):
        """Testa get_by_id amb ID inexistent."""
        service = AcademicCourseService(academic_course_dao)
        
        result = service.get_by_id(999)
        
        assert result is None

    def test_get_by_course(self, academic_course_dao, db):
        """Testa get_by_course amb un curs existent."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear curs
        db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        
        result = service.get_by_course("2024-2025")
        
        assert result is not None
        assert result.course == "2024-2025"

    def test_get_by_course_not_found(self, academic_course_dao, db):
        """Testa get_by_course amb nom inexistent."""
        service = AcademicCourseService(academic_course_dao)
        
        result = service.get_by_course("2030-2031")
        
        assert result is None

    def test_get_or_create_existing(self, academic_course_dao, db):
        """Testa get_or_create quan el curs ja existeix."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear curs existent
        existing = db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        
        result = service.get_or_create("2024-2025")
        
        assert result.id == existing.id
        assert result.course == "2024-2025"

    def test_get_or_create_new(self, academic_course_dao, db):
        """Testa get_or_create quan el curs no existeix."""
        service = AcademicCourseService(academic_course_dao)
        
        result = service.get_or_create("2024-2025")
        
        assert result is not None
        assert result.course == "2024-2025"
        
        # Verificar que s'ha creat
        all_courses = service.get_all()
        assert len(all_courses) == 1
        assert all_courses[0].course == "2024-2025"

    def test_create(self, academic_course_dao, db):
        """Testa la creació d'un nou curs."""
        service = AcademicCourseService(academic_course_dao)
        
        new_course = service.create(AcademicCourseNew(course="2026-2027"))
        
        assert new_course.id is not None
        assert new_course.course == "2026-2027"
        
        # Verificar que existeix a la BD
        all_courses = db.academic_courses.get_all()
        assert len(all_courses) == 1
        assert all_courses[0].course == "2026-2027"

    def test_create_duplicate_course(self, academic_course_dao, db):
        """Testa que no es pot crear un curs amb nom duplicat."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear primer curs
        db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        
        # Intentar crear-ne un altre amb el mateix nom
        with pytest.raises(ValueError, match="Ja existeix un curs acadèmic amb el nom '2024-2025'"):
            service.create(AcademicCourseNew(course="2024-2025"))

    def test_delete(self, academic_course_dao, db):
        """Testa l'eliminació d'un curs."""
        service = AcademicCourseService(academic_course_dao)
        
        # Crear curs
        created = db.academic_courses.create(AcademicCourseNew(course="2024-2025"))
        
        # Eliminar
        service.delete(created.id)
        
        # Verificar que ja no existeix
        result = service.get_by_id(created.id)
        assert result is None

    def test_update(self, academic_course_dao, db):
        service = AcademicCourseService(academic_course_dao)
        created = service.create(AcademicCourseNew("2024-2025"))

        updated = service.update(AcademicCourse(created.id, "2025-2026"))

        assert updated.course == "2025-2026"
        assert service.get_by_id(created.id).course == "2025-2026"

    @pytest.mark.parametrize("course", ["2026", "2026-2028", "abcd-efgh"])
    def test_create_rebutja_format_invalid(self, academic_course_dao, db, course):
        service = AcademicCourseService(academic_course_dao)
        with pytest.raises(ValidationError):
            service.create(AcademicCourseNew(course))

    def test_delete_rebutja_curs_en_us(self, academic_course_dao, db):
        from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew

        service = AcademicCourseService(academic_course_dao)
        course = service.create(AcademicCourseNew("2025-2026"))
        category = db.categories.create(CategoryNew("Acadèmic"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.notes.create(NoteNew(
            student.id, category.id, "2026-01-01", course.id, "Nota"
        ))

        assert service.can_delete(course.id) is False
        with pytest.raises(EntityInUseError):
            service.delete(course.id)
