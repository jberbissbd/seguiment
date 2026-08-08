import uuid
import pytest
from tutopy.models.messaging import Student, StudentNew, Contact, ContactNew, StudentDocument, StudentDocumentNew
from tutopy.services.student_service import StudentService


class TestStudentService:
    """Tests per a StudentService."""

    def test_create_student_valid(self, student_dao, contact_dao, document_dao, db):
        """Testa la creació d'un alumne vàlid."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Dades vàlides
        student_data = StudentNew(
            uuid=str(uuid.uuid4()),
            name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        
        # Executar
        created_student = service.create_student(student_data)
        
        # Verificar
        assert created_student.id is not None
        assert created_student.uuid is not None  # El DAO genera un nou UUID
        assert created_student.name == "Jordi"
        assert created_student.surnames == "Garcia López"
        assert created_student.group_name == "4t A"

    def test_create_student_multiple(self, student_dao, contact_dao, document_dao, db):
        """Testa la creació de múltiples alumnes."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear diversos alumnes
        student1 = service.create_student(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Anna",
            surnames="Martínez Sánchez",
            group_name="3r B"
        ))
        student2 = service.create_student(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Pere",
            surnames="López García",
            group_name="2n A"
        ))
        
        # Verificar
        assert student1.id != student2.id
        assert len(db.students.get_all()) == 2

    def test_get_student_with_contacts_no_contacts(self, student_dao, contact_dao, document_dao, db):
        """Testa l'obtenció d'un alumne sense contactes ni documents."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear un alumne sense contactes ni documents
        student_data = StudentNew(
            uuid=str(uuid.uuid4()),
            name="Maria",
            surnames="Sánchez Pérez",
            group_name="1r A"
        )
        created_student = db.students.create(student_data)
        
        # Executar
        student_with_contacts = service.get_student_with_contacts(created_student.id)
        
        # Verificar
        assert student_with_contacts is not None
        assert student_with_contacts.id == created_student.id
        assert hasattr(student_with_contacts, 'contacts')
        assert hasattr(student_with_contacts, 'documents')
        assert student_with_contacts.contacts == []
        assert student_with_contacts.documents == []

    def test_get_student_with_contacts_with_contacts(self, student_dao, contact_dao, document_dao, db):
        """Testa l'obtenció d'un alumne amb contactes associats."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear un alumne
        student_data = StudentNew(
            uuid=str(uuid.uuid4()),
            name="Jordi",
            surnames="Garcia López",
            group_name="4t A"
        )
        created_student = db.students.create(student_data)
        
        # Afegir contactes a l'alumne
        contact1 = db.contacts.create(ContactNew(
            student_id=created_student.id,
            name="Joan García",
            description="Pare",
            phone="999111222",
            email="joan@example.com"
        ))
        contact2 = db.contacts.create(ContactNew(
            student_id=created_student.id,
            name="Anna López",
            description="Mare",
            phone="999333444",
            email="anna@example.com"
        ))
        
        # Executar
        student_with_contacts = service.get_student_with_contacts(created_student.id)
        
        # Verificar
        assert student_with_contacts is not None
        assert student_with_contacts.id == created_student.id
        assert len(student_with_contacts.contacts) == 2
        assert all(c.student_id == created_student.id for c in student_with_contacts.contacts)

    def test_get_student_with_contacts_with_documents(self, student_dao, contact_dao, document_dao, db):
        """Testa l'obtenció d'un alumne amb documents associats."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear un alumne
        student_data = StudentNew(
            uuid=str(uuid.uuid4()),
            name="Pere",
            surnames="López Martínez",
            group_name="2n B"
        )
        created_student = db.students.create(student_data)
        
        # Afegir documents a l'alumne
        doc1 = db.documents.create(StudentDocumentNew(
            student_id=created_student.id,
            name="Document 1",
            description="Informe mèdic",
            uuid_filename=str(uuid.uuid4()),
            original_filename="informe1.pdf",
            file_path="/path/informe1.pdf"
        ))
        doc2 = db.documents.create(StudentDocumentNew(
            student_id=created_student.id,
            name="Document 2",
            description="Autorització",
            uuid_filename=str(uuid.uuid4()),
            original_filename="autoritzacio.pdf",
            file_path="/path/autoritzacio.pdf"
        ))
        
        # Executar
        student_with_contacts = service.get_student_with_contacts(created_student.id)
        
        # Verificar
        assert student_with_contacts is not None
        assert student_with_contacts.id == created_student.id
        assert len(student_with_contacts.documents) == 2
        assert all(d.student_id == created_student.id for d in student_with_contacts.documents)

    def test_get_student_with_contacts_complete(self, student_dao, contact_dao, document_dao, db):
        """Testa l'obtenció d'un alumne amb contactes i documents."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear un alumne
        student_data = StudentNew(
            uuid=str(uuid.uuid4()),
            name="Anna",
            surnames="Martínez Sánchez",
            group_name="3r A"
        )
        created_student = db.students.create(student_data)
        
        # Afegir contactes
        db.contacts.create(ContactNew(
            student_id=created_student.id,
            name="Toni Martínez",
            description="Pare",
            phone="999555666",
            email="toni@example.com"
        ))
        
        # Afegir documents
        db.documents.create(StudentDocumentNew(
            student_id=created_student.id,
            name="Certificat",
            description="Certificat de notes",
            uuid_filename=str(uuid.uuid4()),
            original_filename="certificat.pdf",
            file_path="/path/certificat.pdf"
        ))
        
        # Executar
        student_with_contacts = service.get_student_with_contacts(created_student.id)
        
        # Verificar
        assert student_with_contacts is not None
        assert student_with_contacts.id == created_student.id
        assert len(student_with_contacts.contacts) == 1
        assert len(student_with_contacts.documents) == 1

    def test_get_student_with_contacts_nonexistent(self, student_dao, contact_dao, document_dao, db):
        """Testa l'obtenció d'un alumne inexistent."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Executar amb ID inexistent
        result = service.get_student_with_contacts(99999)
        
        # Verificar
        assert result is None

    def test_get_student_with_contacts_other_student_contacts(self, student_dao, contact_dao, document_dao, db):
        """Testa que els contactes i documents són només els de l'alumne especificat."""
        service = StudentService(student_dao, contact_dao, document_dao)
        
        # Crear dos alumnes
        student1 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Alumne1",
            surnames="Test1",
            group_name="4t A"
        ))
        student2 = db.students.create(StudentNew(
            uuid=str(uuid.uuid4()),
            name="Alumne2",
            surnames="Test2",
            group_name="4t A"
        ))
        
        # Afegir contactes i documents a student1
        db.contacts.create(ContactNew(
            student_id=student1.id,
            name="Contacte1",
            description="Pare",
            phone="111",
            email="c1@example.com"
        ))
        db.documents.create(StudentDocumentNew(
            student_id=student1.id,
            name="Doc1",
            description="Doc 1",
            uuid_filename=str(uuid.uuid4()),
            original_filename="doc1.pdf",
            file_path="/path/doc1.pdf"
        ))
        
        # Afegir contactes i documents a student2
        db.contacts.create(ContactNew(
            student_id=student2.id,
            name="Contacte2",
            description="Mare",
            phone="222",
            email="c2@example.com"
        ))
        db.documents.create(StudentDocumentNew(
            student_id=student2.id,
            name="Doc2",
            description="Doc 2",
            uuid_filename=str(uuid.uuid4()),
            original_filename="doc2.pdf",
            file_path="/path/doc2.pdf"
        ))
        
        # Obtenir student1 amb contactes i documents
        student1_with_data = service.get_student_with_contacts(student1.id)
        
        # Verificar que només té els seus propis
        assert len(student1_with_data.contacts) == 1
        assert len(student1_with_data.documents) == 1
        assert student1_with_data.contacts[0].name == "Contacte1"
        assert student1_with_data.documents[0].name == "Doc1"
