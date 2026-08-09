from typing import Optional
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew
from tutopy.services.exceptions import (
    DuplicateEntityError, EntityInUseError, EntityNotFoundError,
)
from tutopy.services.validation_service import ValidationService


class AcademicCourseService:
    """Servei per gestionar cursos acadèmics.
    
    Proporciona una capa d'abstracció sobre AcademicCourseDAO amb
    lògica de negoci addicional.
    """

    def __init__(self, academic_course_dao: AcademicCourseDAO,
        validation_service: ValidationService = None):
        self.academic_course_dao = academic_course_dao
        self.validation_service = validation_service or ValidationService()

    def get_all(self) -> list[AcademicCourse]:
        """Retorna tots els cursos acadèmics ordenats per any (descendent)."""
        return self.academic_course_dao.get_all()

    def get_by_id(self, id: int) -> Optional[AcademicCourse]:
        """Retorna un curs acadèmic pel seu ID, o None si no existeix."""
        return self.academic_course_dao.get_by_id(id)

    def get_by_course(self, course: str) -> Optional[AcademicCourse]:
        """Retorna un curs acadèmic pel seu nom (ex: '2026-2027').
        
        Args:
            course: Nom del curs en format YYYY-YYYY.
            
        Returns:
            AcademicCourse o None si no existeix.
        """
        return self.academic_course_dao.get_by_course(course)

    def get_or_create(self, course: str) -> AcademicCourse:
        """Retorna un curs acadèmic existent o el crea si no existeix.
        
        Args:
            course: Nom del curs en format YYYY-YYYY.
            
        Returns:
            AcademicCourse: El curs existent o el nou creat.
        """
        course = self.validation_service.academic_course(course)
        return self.academic_course_dao.get_or_create(course)

    def create(self, data: AcademicCourseNew) -> AcademicCourse:
        """Crea un nou curs acadèmic.
        
        Args:
            data: Dades del nou curs (nom).
            
        Returns:
            AcademicCourse: El curs creat.
            
        Raises:
            ValueError: Si ja existeix un curs amb el mateix nom.
        """
        course = self.validation_service.academic_course(data.course)
        existing = self.academic_course_dao.get_by_course(course)
        if existing:
            raise DuplicateEntityError(
                f"Ja existeix un curs acadèmic amb el nom '{course}'"
            )
        return self.academic_course_dao.create(AcademicCourseNew(course))

    def can_delete(self, id: int) -> bool:
        return self.academic_course_dao.is_deletable(id)

    def delete(self, id: int) -> None:
        """Elimina un curs acadèmic pel seu ID.
        
        Args:
            id: ID del curs a eliminar.
        """
        if self.academic_course_dao.get_by_id(id) is None:
            raise EntityNotFoundError(f"No existeix el curs acadèmic amb ID {id}")
        if not self.can_delete(id):
            raise EntityInUseError("No es pot eliminar: el curs acadèmic està en ús.")
        self.academic_course_dao.delete(id)
