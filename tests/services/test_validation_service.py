import uuid
import pytest
from tutopy.models.messaging import StudentNew, NoteNew, CategoryNew, AcademicCourseNew
from tutopy.services.validation_service import ValidationService


class TestValidationService:
    """Tests per a ValidationService."""

    def test_validate_student_valid(self, category_dao, db):
        """Testa la validació d'un alumne vàlid."""
        # Crear el servei
        service = ValidationService(category_dao)
        
        # Dades vàlides
        student_data = StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        
        # No hauria de llançar cap excepció
        service.validate_student(student_data)

    def test_validate_student_empty_name(self, category_dao, db):
        """Testa que la validació falla si el nom està buit."""
        service = ValidationService(category_dao)
        
        student_data = StudentNew(name="",
            surnames="Garcia López",
            group_name="4t A"
        )
        
        with pytest.raises(ValueError, match="El nom de l'alumne no pot estar buit"):
            service.validate_student(student_data)

    def test_validate_student_none_name(self, category_dao, db):
        """Testa que la validació falla si el nom és None."""
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo per bypassar el dataclass
        student = StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        student.name = None
        
        with pytest.raises(ValueError, match="El nom de l'alumne no pot estar buit"):
            service.validate_student(student)

    def test_validate_student_non_string_name(self, category_dao, db):
        """Testa que la validació falla si el nom no és una cadena."""
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo
        student = StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        student.name = 123  # No és string
        
        with pytest.raises(ValueError, match="El nom de l'alumne no pot estar buit"):
            service.validate_student(student)

    def test_validate_student_empty_surnames(self, category_dao, db):
        """Testa que la validació falla si els cognoms estan buits."""
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo
        student = StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        student.surnames = ""
        
        with pytest.raises(ValueError, match="Els cognoms no poden estar buits"):
            service.validate_student(student)

    def test_validate_student_non_string_surnames(self, category_dao, db):
        """Testa que la validació falla si els cognoms no són text."""
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo
        student = StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        student.surnames = 456
        
        with pytest.raises(ValueError, match="Els cognoms no poden estar buits"):
            service.validate_student(student)

    def test_validate_note_valid(self, category_dao, db):
        """Testa la validació d'una nota vàlida."""
        # Crear una categoria existent
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        
        # Crear el servei
        service = ValidationService(category_dao)
        
        # Dades vàlides
        note_data = NoteNew(
            student_id=1,
            category_id=categoria.id,
            date="2026-01-15",
            course_id=1,
            content="Nota de prova"
        )
        
        # No hauria de llançar cap excepció
        service.validate_note(note_data)

    def test_validate_note_empty_content(self, category_dao, db):
        """Testa que la validació falla si el contingut està buit."""
        # Crear una categoria existent
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo
        note = NoteNew(
            student_id=1,
            category_id=categoria.id,
            date="2026-01-15",
            course_id=1,
            content="Nota de prova"
        )
        note.content = ""
        
        with pytest.raises(ValueError, match="El contingut de la nota no pot estar buit"):
            service.validate_note(note)

    def test_validate_note_none_content(self, category_dao, db):
        """Testa que la validació falla si el contingut és None."""
        # Crear una categoria existent
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo
        note = NoteNew(
            student_id=1,
            category_id=categoria.id,
            date="2026-01-15",
            course_id=1,
            content="Nota de prova"
        )
        note.content = None
        
        with pytest.raises(ValueError, match="El contingut de la nota no pot estar buit"):
            service.validate_note(note)

    def test_validate_note_nonexistent_category(self, category_dao, db):
        """Testa que la validació falla si la categoria no existeix."""
        service = ValidationService(category_dao)
        
        # Crear un objecte vàlid i després modificar-lo per utilitzar una categoria inexistent
        note = NoteNew(
            student_id=1,
            category_id=99999,  # ID no existent
            date="2026-01-15",
            course_id=1,
            content="Nota amb categoria inexistent"
        )
        
        with pytest.raises(ValueError, match="La categoria amb ID 99999 no existeix"):
            service.validate_note(note)

    def test_can_delete_category_true(self, category_dao, db):
        """Testa que can_delete_category retorna True per una categoria sense notes."""
        # Crear una categoria sense notes associades
        categoria = db.categories.create(CategoryNew("Esport"))
        
        # Crear el servei
        service = ValidationService(category_dao)
        
        # Verificar que es pot eliminar
        assert service.can_delete_category(categoria.id) is True

    def test_can_delete_category_false(self, category_dao, db):
        """Testa que can_delete_category retorna False per una categoria amb notes."""
        # Crear una categoria
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        
        # Crear un curs i un alumne per poder crear una nota
        from tutopy.models.messaging import AcademicCourseNew
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear una nota que usa aquesta categoria
        db.notes.create(NoteNew(
            student_id=alumne.id,
            category_id=categoria.id,
            date="2026-01-15",
            course_id=curs.id,
            content="Nota de prova"
        ))
        
        # Crear el servei
        service = ValidationService(category_dao)
        
        # Verificar que NO es pot eliminar
        assert service.can_delete_category(categoria.id) is False
