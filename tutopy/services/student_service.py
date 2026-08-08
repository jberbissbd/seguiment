from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.models.messaging import Student, StudentNew, Contact, ContactNew, StudentDocument, StudentDocumentNew

class StudentService:
    def __init__(self, student_dao: StudentDAO, contact_dao: ContactDAO, document_dao: DocumentDAO):
        self.student_dao = student_dao
        self.contact_dao = contact_dao
        self.document_dao = document_dao

    def create_student(self, student_data: StudentNew) -> Student:
        """Crea un alumne i valida les dades (usant la validació de StudentNew)."""
        # La validació ja es fa automàticament al crear StudentNew
        return self.student_dao.create(student_data)

    def get_student_with_contacts(self, student_id: int) -> Student:
        """Obté un alumne amb els seus contactes i documents."""
        student = self.student_dao.get_by_id(student_id)
        if student:
            student.contacts = self.contact_dao.get_by_student(student_id)  # Llista de Contact
            student.documents = self.document_dao.get_by_student(student_id)  # Llista de StudentDocument
        return student