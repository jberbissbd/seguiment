"""
Controlador d'alumnes.

Actua com a mediador entre la vista i els serveis relacionats amb alumnes.
"""

from typing import Optional
from PySide6.QtCore import Signal, QObject

from tutopy.models.messaging import Student, StudentNew
from tutopy.services.student_service import StudentService
from tutopy.services.category_service import CategoryService
from tutopy.services.academic_course_service import AcademicCourseService


class StudentController(QObject):
    """Controlador per gestionar alumnes."""
    
    # Senyals
    student_created = Signal(Student)
    student_updated = Signal(Student)
    student_deleted = Signal(int)
    students_loaded = Signal(list)
    
    def __init__(
        self,
        student_service: StudentService,
        category_service: CategoryService,
        academic_course_service: AcademicCourseService
    ):
        """
        Inicialitza el controlador.
        
        Args:
            student_service: Servei d'alumnes
            category_service: Servei de categories
            academic_course_service: Servei de cursos acadèmics
        """
        super().__init__()
        self.student_service = student_service
        self.category_service = category_service
        self.academic_course_service = academic_course_service

    def load_students(self) -> list[Student]:
        """
        Carrega tots els alumnes.
        
        Returns:
            Llista de tots els alumnes
        """
        students = self.student_service.get_all()
        self.students_loaded.emit(students)
        return students

    def search_students(self, query: str) -> list[Student]:
        """
        Cerca alumnes segons una consulta de text.
        
        Args:
            query: Text de cerca
            
        Returns:
            Llista d'alumnes que coincidixen amb la consulta
        """
        return self.student_service.search(query)

    def get_student(self, student_id: int) -> Optional[Student]:
        """
        Obté un alumne pel seu ID.
        
        Args:
            student_id: ID de l'alumne
            
        Returns:
            L'alumne o None si no existeix
        """
        return self.student_service.get_student_by_id(student_id)

    def get_student_with_details(self, student_id: int) -> Optional[Student]:
        """
        Obté un alumne amb tots els seus detalls (contactes, documents, etc.).
        
        Args:
            student_id: ID de l'alumne
            
        Returns:
            L'alumne amb detalls o None si no existeix
        """
        return self.student_service.get_student_with_contacts(student_id)

    def create_student(self, data: StudentNew) -> Student:
        """
        Crea un nou alumne.
        
        Args:
            data: Dades del nou alumne
            
        Returns:
            L'alumne creat
        """
        student = self.student_service.create_student(data)
        self.student_created.emit(student)
        return student

    def update_student(self, student_id: int, data: StudentNew) -> Optional[Student]:
        """
        Actualitza un alumne existent.
        
        Args:
            student_id: ID de l'alumne a actualitzar
            data: Noves dades de l'alumne
            
        Returns:
            L'alumne actualitzat o None
        """
        # TODO: Implementar al StudentService
        # student = self.student_service.update(student_id, data)
        # self.student_updated.emit(student)
        # return student
        raise NotImplementedError("update_student no està implementat al servei")

    def delete_student(self, student_id: int) -> bool:
        """
        Elimina un alumne.
        
        Args:
            student_id: ID de l'alumne a eliminar
            
        Returns:
            True si s'ha eliminat correctament, False en cas contrari
        """
        try:
            self.student_service.delete(student_id)
            self.student_deleted.emit(student_id)
            return True
        except Exception:
            return False

    def get_all_groups(self) -> list[str]:
        """
        Obté una llista de tots els grups d'alumnes.
        
        Returns:
            Llista de noms de grups
        """
        return self.student_service.get_groups()

    def change_student_group(
        self,
        student_id: int,
        new_group: str,
        change_date: str = None,
        academic_course_id: int = None
    ):
        """
        Canvia el grup d'un alumne.
        
        Args:
            student_id: ID de l'alumne
            new_group: Nou nom del grup
            change_date: Data del canvi (format YYYY-MM-DD)
            academic_course_id: ID del curs acadèmic
        """
        return self.student_service.change_student_group(
            student_id, new_group, change_date, academic_course_id
        )

    def get_current_group(self, student_id: int) -> Optional[str]:
        """
        Obté el grup actual d'un alumne.
        
        Args:
            student_id: ID de l'alumne
            
        Returns:
            Nom del grup actual o None
        """
        return self.student_service.get_current_group(student_id)

    def get_group_history(self, student_id: int) -> list:
        """
        Obté l'històric de grups d'un alumne.
        
        Args:
            student_id: ID de l'alumne
            
        Returns:
            Llista amb l'històric de grups
        """
        return self.student_service.get_group_history(student_id)
