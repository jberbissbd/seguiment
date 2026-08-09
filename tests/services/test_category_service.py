import pytest
from tutopy.services.category_service import CategoryService
from tutopy.services.validation_service import ValidationService
from tutopy.models.messaging import AcademicCourseNew, Category, CategoryNew


class TestCategoryService:
    """Tests per a CategoryService amb base de dades real."""

    def test_get_all_empty(self, category_dao, db):
        """Testa get_all quan no hi ha categories."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        result = service.get_all()
        assert result == []

    def test_get_all_with_categories(self, category_dao, db):
        """Testa get_all amb categories existents."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categories directament a la BD
        cat1 = db.categories.create(CategoryNew(name="Conducta"))
        cat2 = db.categories.create(CategoryNew(name="Acadèmic"))
        
        result = service.get_all()
        
        assert len(result) == 2
        assert {c.name for c in result} == {"Conducta", "Acadèmic"}

    def test_get_by_id(self, category_dao, db):
        """Testa get_by_id amb una categoria existent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria
        created = db.categories.create(CategoryNew(name="Test"))
        
        result = service.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "Test"

    def test_get_by_id_not_found(self, category_dao, db):
        """Testa get_by_id amb ID inexistent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        result = service.get_by_id(999)
        
        assert result is None

    def test_get_by_name(self, category_dao, db):
        """Testa get_by_name amb una categoria existent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria
        db.categories.create(CategoryNew(name="Conducta"))
        
        result = service.get_by_name("Conducta")
        
        assert result is not None
        assert result.name == "Conducta"

    def test_get_by_name_not_found(self, category_dao, db):
        """Testa get_by_name amb nom inexistent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        result = service.get_by_name("Inexistent")
        
        assert result is None

    def test_create(self, category_dao, db):
        """Testa la creació d'una nova categoria."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        new_category = service.create(CategoryNew(name="Nova Categoria"))
        
        assert new_category.id is not None
        assert new_category.name == "Nova Categoria"
        
        # Verificar que existeix a la BD
        all_categories = db.categories.get_all()
        assert len(all_categories) == 1
        assert all_categories[0].name == "Nova Categoria"

    def test_create_duplicate_name(self, category_dao, db):
        """Testa que no es pot crear una categoria amb nom duplicat."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear primera categoria
        db.categories.create(CategoryNew(name="Conducta"))
        
        # Intentar crear-ne una altra amb el mateix nom
        with pytest.raises(ValueError, match="Ja existeix una categoria amb el nom 'Conducta'"):
            service.create(CategoryNew(name="Conducta"))

    def test_rename(self, category_dao, db):
        """Testa el renom d'una categoria."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria
        created = db.categories.create(CategoryNew(name="Antic Nom"))
        
        # Renomenar
        updated_category = Category(id=created.id, name="Nou Nom")
        service.rename(updated_category)
        
        # Verificar el canvi
        result = service.get_by_id(created.id)
        assert result.name == "Nou Nom"

    def test_rename_nonexistent(self, category_dao, db):
        """Testa que no es pot renomenar una categoria inexistent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        nonexistent_category = Category(id=999, name="Nou Nom")
        
        with pytest.raises(ValueError, match="No existeix la categoria amb ID 999"):
            service.rename(nonexistent_category)

    def test_rename_duplicate_name(self, category_dao, db):
        """Testa que no es pot renomenar a un nom ja existent."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear dues categories
        cat1 = db.categories.create(CategoryNew(name="Categ1"))
        db.categories.create(CategoryNew(name="Categ2"))
        
        # Intentar renomenar cat1 a "Categ2"
        updated_category = Category(id=cat1.id, name="Categ2")
        
        with pytest.raises(ValueError, match="Ja existeix una categoria amb el nom 'Categ2'"):
            service.rename(updated_category)

    def test_can_delete_true(self, category_dao, db):
        """Testa can_delete amb una categoria sense notes."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria sense notes
        created = db.categories.create(CategoryNew(name="Test"))
        
        result = service.can_delete(created.id)
        
        assert result is True

    def test_can_delete_false(self, category_dao, note_dao, db):
        """Testa can_delete amb una categoria amb notes."""
        from tutopy.models.messaging import StudentNew, NoteNew
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria i una nota que l'usa
        category = db.categories.create(CategoryNew(name="Test"))
        student = db.students.create(StudentNew(name="Test",
            surnames="User",
            group_name="1r A"
        ))
        course = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        db.notes.create(NoteNew(
            student_id=student.id,
            category_id=category.id,
            date="2026-01-01",
            course_id=course.id,
            content="Test note"
        ))
        
        result = service.can_delete(category.id)
        
        assert result is False

    def test_delete(self, category_dao, db):
        """Testa l'eliminació d'una categoria sense notes."""
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria
        created = db.categories.create(CategoryNew(name="Test"))
        
        # Eliminar
        service.delete(created.id)
        
        # Verificar que ja no existeix
        result = service.get_by_id(created.id)
        assert result is None

    def test_delete_with_notes(self, category_dao, note_dao, db):
        """Testa que no es pot eliminar una categoria amb notes."""
        from tutopy.models.messaging import StudentNew, NoteNew
        service = CategoryService(category_dao, ValidationService(category_dao))
        
        # Crear categoria i una nota que l'usa
        category = db.categories.create(CategoryNew(name="Test"))
        student = db.students.create(StudentNew(name="Test",
            surnames="User",
            group_name="1r A"
        ))
        course = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        db.notes.create(NoteNew(
            student_id=student.id,
            category_id=category.id,
            date="2026-01-01",
            course_id=course.id,
            content="Test note"
        ))
        
        with pytest.raises(ValueError, match="No es pot eliminar: la categoria té notes associades"):
            service.delete(category.id)

    def test_rename_categoria_amb_notes(self, category_dao, db):
        """Renomenar és segur perquè les notes referencien l'ID."""
        from tutopy.models.messaging import StudentNew, NoteNew
        service = CategoryService(category_dao)
        category = db.categories.create(CategoryNew("Antiga"))
        student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        course = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        db.notes.create(NoteNew(
            student.id, category.id, "2026-01-01", course.id, "Nota"
        ))

        service.rename(Category(category.id, "Nova"))

        assert service.get_by_id(category.id).name == "Nova"
