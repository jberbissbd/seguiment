from typing import Optional
from tutopy.database.daos.annotation_dao import AnnotationDAO
from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew


class AnnotationService:
    """Servei per gestionar anotacions d'alumnes.
    
    Proporciona una capa d'abstracció sobre AnnotationDAO amb
    lògica de negoci addicional.
    """

    def __init__(self, annotation_dao: AnnotationDAO):
        self.annotation_dao = annotation_dao

    def get_by_student(self, student_id: int) -> list[StudentAnnotation]:
        """Retorna totes les anotacions d'un alumne ordenades per ID.
        
        Args:
            student_id: ID de l'alumne.
            
        Returns:
            list[StudentAnnotation]: Llista d'anotacions de l'alumne.
        """
        return self.annotation_dao.get_by_student(student_id)

    def create(self, data: StudentAnnotationNew) -> StudentAnnotation:
        """Crea una nova anotació per a un alumne.
        
        Args:
            data: Dades de la nova anotació (student_id, content).
            
        Returns:
            StudentAnnotation: L'anotació creada.
        """
        return self.annotation_dao.create(data)

    def update(self, annotation: StudentAnnotation) -> None:
        """Actualitza una anotació existent.
        
        Args:
            annotation: StudentAnnotation amb les dades actualitzades.
        """
        self.annotation_dao.update(annotation)

    def delete(self, id: int) -> None:
        """Elimina una anotació pel seu ID.
        
        Args:
            id: ID de l'anotació a eliminar.
        """
        self.annotation_dao.delete(id)
