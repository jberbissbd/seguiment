from typing import Optional
from tutopy.database.daos.annotation_dao import AnnotationDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew
from tutopy.services.exceptions import EntityNotFoundError
from tutopy.services.validation_service import ValidationService


class AnnotationService:
    """Servei per gestionar anotacions d'alumnes.
    
    Proporciona una capa d'abstracció sobre AnnotationDAO amb
    lògica de negoci addicional.
    """

    def __init__(self, annotation_dao: AnnotationDAO, student_dao: StudentDAO,
        validation_service: ValidationService = None):
        self.annotation_dao = annotation_dao
        self.student_dao = student_dao
        self.validation_service = validation_service or ValidationService()

    def get_by_student(self, student_id: int) -> list[StudentAnnotation]:
        """Retorna totes les anotacions d'un alumne ordenades per ID.
        
        Args:
            student_id: ID de l'alumne.
            
        Returns:
            list[StudentAnnotation]: Llista d'anotacions de l'alumne.
        """
        self._require_student(student_id)
        return self.annotation_dao.get_by_student(student_id)

    def get_by_id(self, annotation_id: int) -> StudentAnnotation:
        self.validation_service.positive_id(annotation_id)
        annotation = self.annotation_dao.get_by_id(annotation_id)
        if annotation is None:
            raise EntityNotFoundError(
                f"El descriptor amb ID {annotation_id} no existeix."
            )
        return annotation

    def create(self, data: StudentAnnotationNew) -> StudentAnnotation:
        """Crea una nova anotació per a un alumne.
        
        Args:
            data: Dades de la nova anotació (student_id, content).
            
        Returns:
            StudentAnnotation: L'anotació creada.
        """
        self._require_student(data.student_id)
        content = self.validation_service.required_text(
            data.content, "El contingut del descriptor no pot estar buit."
        )
        return self.annotation_dao.create(StudentAnnotationNew(data.student_id, content))

    def update(self, annotation: StudentAnnotation) -> None:
        """Actualitza una anotació existent.
        
        Args:
            annotation: StudentAnnotation amb les dades actualitzades.
        """
        existing = self.get_by_id(annotation.id)
        content = self.validation_service.required_text(
            annotation.content, "El contingut del descriptor no pot estar buit."
        )
        self._require_student(annotation.student_id)
        self.annotation_dao.update(StudentAnnotation(
            annotation.id, existing.student_id, content
        ))

    def delete(self, id: int) -> None:
        """Elimina una anotació pel seu ID.
        
        Args:
            id: ID de l'anotació a eliminar.
        """
        self.get_by_id(id)
        self.annotation_dao.delete(id)

    def _require_student(self, student_id: int):
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
