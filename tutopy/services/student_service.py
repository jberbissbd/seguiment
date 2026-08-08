from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.models.messaging import Student, StudentNew, Contact, ContactNew, StudentDocument, StudentDocumentNew, StudentGroupHistory
from datetime import datetime
from typing import Optional


class StudentService:
    def __init__(self, student_dao: StudentDAO, contact_dao: ContactDAO, document_dao: DocumentDAO, group_history_dao: StudentGroupHistoryDAO):
        self.student_dao = student_dao
        self.contact_dao = contact_dao
        self.document_dao = document_dao
        self.group_history_dao = group_history_dao

    def create_student(self, student_data: StudentNew) -> Student:
        """Crea un alumne i valida les dades (usant la validació de StudentNew)."""
        # La validació ja es fa automàticament al crear StudentNew
        return self.student_dao.create(student_data)

    def get_student_with_contacts(self, student_id: int) -> Student:
        """Obté un alumne amb els seus contactes i documents."""
        student = self.student_dao.get_by_id(student_id)
        if student:
            student.contacts = self.contact_dao.get_by_student(student_id)
            student.documents = self.document_dao.get_by_student(student_id)
        return student

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

        # Obtenir el grup actual per tancar-lo
        current_history = self.group_history_dao.get_current(student_id)
        if current_history:
            current_history.end_date = change_date
            self.group_history_dao.update(current_history)

        # Resoldre el curs acadèmic si no s'especifica
        if academic_course_id is None:
            from tutopy.services.utils import AcademicCourseDeterminator
            course_str = AcademicCourseDeterminator().curs_academic_singular(change_date)
            academic_course_id = self.group_history_dao.conn.execute(
                "SELECT id FROM academic_courses WHERE course = ?", (course_str,)
            ).fetchone()
            academic_course_id = academic_course_id[0] if academic_course_id else None

        # Crear el nou registre
        from tutopy.models.messaging import StudentGroupHistoryNew
        new_history = StudentGroupHistoryNew(
            student_id=student_id,
            group_name=new_group,
            academic_course_id=academic_course_id,
            start_date=change_date,
            end_date=None  # Es marca com a grup actual
        )
        return self.group_history_dao.create(new_history)