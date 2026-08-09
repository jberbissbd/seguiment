from datetime import datetime
from typing import Optional
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import Student, StudentNew, StudentGroupHistoryNew, StudentGroupHistory
from tutopy.services.exceptions import EntityNotFoundError
from tutopy.services.utils import AcademicCourseDeterminator
from tutopy.services.validation_service import ValidationService



class StudentService:
    def __init__(self, student_dao: StudentDAO, contact_dao: ContactDAO,
        document_dao: DocumentDAO, group_history_dao: StudentGroupHistoryDAO,
        academic_course_dao: AcademicCourseDAO,
        validation_service: ValidationService = None):
        self.student_dao = student_dao
        self.contact_dao = contact_dao
        self.document_dao = document_dao
        self.group_history_dao = group_history_dao
        self.academic_course_dao = academic_course_dao
        self.validation_service = validation_service or ValidationService()

    def get_all(self) -> list[Student]:
        """Retorna tots els alumnes ordenats pel DAO."""
        return self.student_dao.get_all()

    def get_by_id(self, student_id: int) -> Optional[Student]:
        """Retorna un alumne o ``None`` si no existeix."""
        self.validation_service.positive_id(student_id)
        return self.student_dao.get_by_id(student_id)

    def get_by_uuid(self, student_uuid: str) -> Optional[Student]:
        """Retorna un alumne per la seva identitat estable."""
        student_uuid = self.validation_service.required_text(
            student_uuid, "L'UUID de l'alumne no pot estar buit."
        )
        return self.student_dao.get_by_uuid(student_uuid)

    def search(self, query: str) -> list[Student]:
        """Cerca alumnes per nom, cognoms o grup."""
        query = self.validation_service.optional_text(query)
        return self.student_dao.search(query) if query else self.get_all()

    def get_groups(self) -> list[str]:
        """Retorna els grups no buits existents."""
        return self.student_dao.get_groups()

    def create_student(self, student_data: StudentNew) -> Student:
        """Valida i crea un alumne amb un UUID nou generat pel DAO."""
        self.validation_service.validate_student(student_data)
        return self.student_dao.create(student_data)

    def create(self, student_data: StudentNew) -> Student:
        """Àlies CRUD de :meth:`create_student`."""
        return self.create_student(student_data)

    def update(self, student: Student) -> Student:
        """Valida i actualitza un alumne existent, conservant el seu UUID."""
        existing = self._require_student(student.id)
        data = StudentNew(student.name, student.surnames, student.group_name)
        self.validation_service.validate_student(data)
        requested_group = data.group_name
        student.uuid = existing.uuid
        student.name = data.name
        student.surnames = data.surnames
        student.group_name = existing.group_name
        self.student_dao.update(student)
        if requested_group != existing.group_name:
            self.change_student_group(student.id, requested_group)
            student.group_name = requested_group
        return student

    def delete(self, student_id: int) -> None:
        """Elimina un alumne existent i les seves dades dependents."""
        self._require_student(student_id)
        self.student_dao.delete(student_id)

    def get_student_with_contacts(self, student_id: int) -> Student:
        """Obté un alumne amb els seus contactes i documents."""
        student = self.student_dao.get_by_id(student_id)
        if student:
            student.contacts = self.contact_dao.get_by_student(student_id)
            student.documents = self.document_dao.get_by_student(student_id)
        return student

    def get_details(self, student_id: int) -> Optional[Student]:
        """Retorna l'alumne amb contactes i documents associats."""
        return self.get_student_with_contacts(student_id)

    def get_current_group(self, student_id: int) -> Optional[str]:
        """Obté el grup actual d'un alumne (últim registre amb end_date NULL)."""
        history = self.group_history_dao.get_current(student_id)
        return history.group_name if history else None

    def get_group_history(self, student_id: int) -> list[StudentGroupHistory]:
        """Obté tot l'històric de grups d'un alumne, ordenat per data."""
        return self.group_history_dao.get_by_student(student_id)

    def change_student_group(
        self,
        student_id: int,
        new_group: str,
        academic_course_id: Optional[int] = None,
        change_date: Optional[str] = None
    ) -> StudentGroupHistory:
        """
        Canvia el grup d'un alumne.

        Args:
            student_id: ID de l'alumne.
            new_group: Nom del nou grup (ex: "4t A").
            academic_course_id: ID del curs acadèmic. Si no s'especifica, es resol automàticament.
            change_date: Data del canvi (format YYYY-MM-DD). Si no s'especifica, usa avui.

        Returns:
            StudentGroupHistory: El registre creat.
        """
        change_date = change_date or datetime.now().strftime("%Y-%m-%d")
        student = self._require_student(student_id)
        new_group = self.validation_service.required_text(
            new_group, "El grup no pot estar buit."
        )
        self.validation_service.iso_date(change_date)

        # Obtenir el grup actual per tancar-lo
        current_history = self.group_history_dao.get_current(student_id)
        if current_history:
            current_history.end_date = change_date
            self.group_history_dao.update(current_history)

        # Resoldre el curs acadèmic si no s'especifica
        if academic_course_id is None:
            course_str = AcademicCourseDeterminator().curs_academic_singular(change_date)
            academic_course_id = self.academic_course_dao.get_or_create(course_str).id
        elif not self.academic_course_dao.get_by_id(academic_course_id):
            raise EntityNotFoundError(
                f"El curs acadèmic amb ID {academic_course_id} no existeix."
            )

        # Crear el nou registre
        new_history = StudentGroupHistoryNew(
            student_id=student_id,
            group_name=new_group,
            academic_course_id=academic_course_id,
            start_date=change_date,
            end_date=None  # Es marca com a grup actual
        )
        history = self.group_history_dao.create(new_history)
        student.group_name = new_group
        self.student_dao.update(student)
        return history

    def _require_student(self, student_id: int) -> Student:
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
