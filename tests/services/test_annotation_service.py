import pytest
from tutopy.services.annotation_service import AnnotationService
from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew, StudentNew


class TestAnnotationService:
    """Tests per a AnnotationService amb base de dades real."""

    def test_get_by_student_empty(self, annotation_dao, db):
        """Testa get_by_student quan l'alumne no té anotacions."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne sense anotacions
        student = db.students.create(StudentNew(
            uuid="test-uuid-1",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        result = service.get_by_student(student.id)
        
        assert result == []

    def test_get_by_student_with_annotations(self, annotation_dao, db):
        """Testa get_by_student amb anotacions existents."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne i anotacions
        student = db.students.create(StudentNew(
            uuid="test-uuid-2",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        # Afegir anotacions directament a la BD
        annotation1 = db.annotations.create(StudentAnnotationNew(
            student_id=student.id,
            content="Anotació 1"
        ))
        annotation2 = db.annotations.create(StudentAnnotationNew(
            student_id=student.id,
            content="Anotació 2"
        ))
        
        result = service.get_by_student(student.id)
        
        assert len(result) == 2
        assert {a.id for a in result} == {annotation1.id, annotation2.id}
        assert {a.content for a in result} == {"Anotació 1", "Anotació 2"}

    def test_get_by_student_other_student_annotations(self, annotation_dao, db):
        """Testa que només es retornen les anotacions de l'alumne especificat."""
        service = AnnotationService(annotation_dao)
        
        # Crear dos alumnes
        student1 = db.students.create(StudentNew(
            uuid="test-uuid-3",
            name="Test1",
            surnames="User",
            group_name="1r A"
        ))
        student2 = db.students.create(StudentNew(
            uuid="test-uuid-4",
            name="Test2",
            surnames="User",
            group_name="1r B"
        ))
        
        # Afegir anotacions a student1
        db.annotations.create(StudentAnnotationNew(
            student_id=student1.id,
            content="Anotació student1"
        ))
        
        # Afegir anotacions a student2
        db.annotations.create(StudentAnnotationNew(
            student_id=student2.id,
            content="Anotació student2"
        ))
        
        # Obtenir anotacions de student1
        result = service.get_by_student(student1.id)
        
        assert len(result) == 1
        assert result[0].content == "Anotació student1"
        assert result[0].student_id == student1.id

    def test_create(self, annotation_dao, db):
        """Testa la creació d'una nova anotació."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne
        student = db.students.create(StudentNew(
            uuid="test-uuid-5",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        # Crear anotació
        new_annotation = service.create(StudentAnnotationNew(
            student_id=student.id,
            content="Nova anotació"
        ))
        
        assert new_annotation.id is not None
        assert new_annotation.student_id == student.id
        assert new_annotation.content == "Nova anotació"
        
        # Verificar que existeix a la BD
        result = service.get_by_student(student.id)
        assert len(result) == 1
        assert result[0].content == "Nova anotació"

    def test_create_multiple(self, annotation_dao, db):
        """Testa la creació de múltiples anotacions."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne
        student = db.students.create(StudentNew(
            uuid="test-uuid-6",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        # Crear múltiples anotacions
        annotation1 = service.create(StudentAnnotationNew(
            student_id=student.id,
            content="Anotació 1"
        ))
        annotation2 = service.create(StudentAnnotationNew(
            student_id=student.id,
            content="Anotació 2"
        ))
        
        # Verificar que totes existeixen
        result = service.get_by_student(student.id)
        assert len(result) == 2
        assert {a.id for a in result} == {annotation1.id, annotation2.id}

    def test_update(self, annotation_dao, db):
        """Testa l'actualització d'una anotació."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne i una anotació
        student = db.students.create(StudentNew(
            uuid="test-uuid-7",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        annotation = db.annotations.create(StudentAnnotationNew(
            student_id=student.id,
            content="Contingut antic"
        ))
        
        # Actualitzar
        updated_annotation = StudentAnnotation(
            id=annotation.id,
            student_id=student.id,
            content="Contingut nou"
        )
        service.update(updated_annotation)
        
        # Verificar el canvi
        result = service.get_by_student(student.id)
        assert len(result) == 1
        assert result[0].content == "Contingut nou"

    def test_delete(self, annotation_dao, db):
        """Testa l'eliminació d'una anotació."""
        service = AnnotationService(annotation_dao)
        
        # Crear un alumne i una anotació
        student = db.students.create(StudentNew(
            uuid="test-uuid-8",
            name="Test",
            surnames="User",
            group_name="1r A"
        ))
        annotation = db.annotations.create(StudentAnnotationNew(
            student_id=student.id,
            content="Anotació a eliminar"
        ))
        
        # Eliminar
        service.delete(annotation.id)
        
        # Verificar que ja no existeix
        result = service.get_by_student(student.id)
        assert result == []

    def test_delete_nonexistent(self, annotation_dao, db):
        """Testa l'eliminació d'una anotació inexistent (no llança error)."""
        service = AnnotationService(annotation_dao)
        
        # Intentar eliminar una anotació que no existeix
        # El DAO no llança error, simplement no fa res
        service.delete(999)
        
        # No hi ha res a verificar, només que no llança excepció
        assert True
