from typing import Optional
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew


class AcademicCourseService:
    """Servei per gestionar cursos acadèmics.
    
    Proporciona una capa d'abstracció sobre AcademicCourseDAO amb
    lògica de negoci addicional.
    """

    def __init__(self, academic_course_dao: AcademicCourseDAO):
        self.academic_course_dao = academic_course_dao

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
        existing = self.academic_course_dao.get_by_course(data.course)
        if existing:
            raise ValueError(f"Ja existeix un curs acadèmic amb el nom '{data.course}'")
        return self.academic_course_dao.create(data)

    def delete(self, id: int) -> None:
        """Elimina un curs acadèmic pel seu ID.
        
        Args:
            id: ID del curs a eliminar.
        """
        self.academic_course_dao.delete(id)
