import uuid
import pytest
from datetime import datetime
from tutopy.models.messaging import Student, StudentNew, Contact, ContactNew, StudentDocument, StudentDocumentNew, StudentGroupHistory, StudentGroupHistoryNew
from tutopy.services.student_service import StudentService
from tutopy.services.exceptions import EntityNotFoundError


class TestStudentService:
    """Tests per a StudentService."""

    def test_create_student_valid(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa la creació d'un alumne vàlid."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Dades vàlides
        student_data = StudentNew(name="Jordi",
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

    def test_create_student_multiple(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa la creació de múltiples alumnes."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear diversos alumnes
        student1 = service.create_student(StudentNew(name="Anna",
            surnames="Martínez Sánchez",
            group_name="3r B"
        ))
        student2 = service.create_student(StudentNew(name="Pere",
            surnames="López García",
            group_name="2n A"
        ))
        
        # Verificar
        assert student1.id != student2.id
        assert len(db.students.get_all()) == 2

    def test_homonims_tenen_identitats_diferents(self, student_dao, contact_dao,
        document_dao, group_history_dao, academic_course_dao, db):
        service = StudentService(
            student_dao, contact_dao, document_dao, group_history_dao,
            academic_course_dao, db.transaction,
        )
        data = StudentNew("Alex", "Garcia", "2n A")

        first = service.create(data)
        second = service.create(StudentNew("Alex", "Garcia", "2n A"))

        assert first.id != second.id
        assert first.uuid != second.uuid
        assert service.get_by_uuid(first.uuid) == first
        assert service.get_by_uuid(second.uuid) == second
        assert len(service.search("Alex Garcia")) == 2

    def test_crud_i_cerca_a_traves_del_servei(self, student_dao, contact_dao,
        document_dao, group_history_dao, academic_course_dao, db):
        service = StudentService(
            student_dao, contact_dao, document_dao, group_history_dao,
            academic_course_dao, db.transaction,
        )
        created = service.create(StudentNew("  Joana ", " Serra ", " 1r B "))
        original_uuid = created.uuid

        assert service.get_by_id(created.id) == created
        assert service.get_all() == [created]
        assert service.get_groups() == ["1r B"]

        created.name = "Joan"
        created.group_name = "2n B"
        updated = service.update(created)
        assert updated.name == "Joan"
        assert service.get_current_group(created.id) == "2n B"
        assert updated.uuid == original_uuid

        service.delete(created.id)
        assert service.get_all() == []
        with pytest.raises(EntityNotFoundError):
            service.delete(created.id)

    def test_get_student_with_contacts_no_contacts(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa l'obtenció d'un alumne sense contactes ni documents."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne sense contactes ni documents
        student_data = StudentNew(name="Maria",
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

    def test_get_student_with_contacts_with_contacts(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa l'obtenció d'un alumne amb contactes associats."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student_data = StudentNew(name="Jordi",
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

    def test_get_student_with_contacts_with_documents(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa l'obtenció d'un alumne amb documents associats."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student_data = StudentNew(name="Pere",
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

    def test_get_student_with_contacts_complete(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa l'obtenció d'un alumne amb contactes i documents."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student_data = StudentNew(name="Anna",
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

    def test_get_student_with_contacts_nonexistent(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa l'obtenció d'un alumne inexistent."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Executar amb ID inexistent
        result = service.get_student_with_contacts(99999)
        
        # Verificar
        assert result is None

    def test_get_student_with_contacts_other_student_contacts(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa que els contactes i documents són només els de l'alumne especificat."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear dos alumnes
        student1 = db.students.create(StudentNew(name="Alumne1",
            surnames="Test1",
            group_name="4t A"
        ))
        student2 = db.students.create(StudentNew(name="Alumne2",
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


class TestStudentGroupHistory:
    """Tests per als mètodes de gestió de grups dinàmics."""

    def test_change_student_group(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa el canvi de grup d'un alumne."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student = db.students.create(StudentNew(name="Jordi",
            surnames="Garcia López",
            group_name="3r A"
        ))
        
        # Inicialment, no té històric de grups
        assert service.get_current_group(student.id) is None
        
        # Canviar a un nou grup
        change_date = "2026-01-15"
        history = service.change_student_group(
            student_id=student.id,
            new_group="4t A",
            change_date=change_date
        )
        
        # Verificar el registre creat
        assert history is not None
        assert history.student_id == student.id
        assert history.group_name == "4t A"
        assert history.start_date == change_date
        assert history.end_date is None
        
        # Verificar que el grup actual és el nou
        assert service.get_current_group(student.id) == "4t A"
        assert service.get_by_id(student.id).group_name == "4t A"
        assert db.academic_courses.get_by_course("2025-2026") is not None

    def test_change_student_group_multiple_times(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa múltiples canvis de grup d'un alumne."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student = db.students.create(StudentNew(name="Anna",
            surnames="Martínez",
            group_name="2n A"
        ))
        
        # Primer canvi: 2n A → 2n B
        service.change_student_group(
            student_id=student.id,
            new_group="2n B",
            change_date="2025-10-01"
        )
        
        # Segon canvi: 2n B → 3r A (curs següent)
        service.change_student_group(
            student_id=student.id,
            new_group="3r A",
            change_date="2026-09-01"
        )
        
        # Verificar l'històric
        history = service.get_group_history(student.id)
        assert len(history) == 2
        assert history[0].group_name == "2n B"
        assert history[1].group_name == "3r A"
        
        # Verificar el grup actual
        assert service.get_current_group(student.id) == "3r A"

    def test_change_student_group_during_course(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa el canvi de grup DURANT el mateix curs."""
        from tutopy.models.messaging import AcademicCourseNew
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne i un curs
        student = db.students.create(StudentNew(name="Pere",
            surnames="López",
            group_name="4t A"
        ))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        # Canviar de grup durant el curs (ex: de 4t A a 4t B a mitjan curs)
        history1 = service.change_student_group(
            student_id=student.id,
            new_group="4t A",
            academic_course_id=curs.id,
            change_date="2025-09-01"
        )
        
        history2 = service.change_student_group(
            student_id=student.id,
            new_group="4t B",
            academic_course_id=curs.id,
            change_date="2026-01-15"
        )
        
        # Verificar l'històric
        history = service.get_group_history(student.id)
        assert len(history) == 2
        assert history[0].group_name == "4t A"
        assert history[0].end_date == "2026-01-15"
        assert history[1].group_name == "4t B"
        assert history[1].end_date is None
        assert history[1].start_date == "2026-01-15"

    def test_change_student_group_to_next_course(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa el canvi de grup AL CURS SEGÜENT."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne
        student = db.students.create(StudentNew(name="Maria",
            surnames="Sánchez",
            group_name="2n A"
        ))
        
        # Canviar de grup al curs següent (el servei resol el curs automàticament)
        history = service.change_student_group(
            student_id=student.id,
            new_group="3r A",
            change_date="2026-09-01"  # El servei resol que això és curs 2026-2027
        )
        
        # Verificar que s'ha creat el registre amb el curs resolt
        assert history is not None
        assert history.group_name == "3r A"
        assert history.start_date == "2026-09-01"
        
        # Verificar el grup actual
        assert service.get_current_group(student.id) == "3r A"

    def test_get_current_group_no_history(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa que get_current_group retorna None si no hi ha històric."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne sense històric de grups
        student = db.students.create(StudentNew(name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        # No hi ha registres a student_group_history
        assert service.get_current_group(student.id) is None

    def test_get_group_history_empty(self, student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db):
        """Testa que get_group_history retorna llista buida si no hi ha històric."""
        service = StudentService(student_dao, contact_dao, document_dao, group_history_dao, academic_course_dao, db.transaction)
        
        # Crear un alumne sense històric
        student = db.students.create(StudentNew(name="Test",
            surnames="User",
            group_name="1r A"
        ))
        
        # Obtenir històric
        history = service.get_group_history(student.id)
        assert history == []

    def test_change_group_es_atomic(self, student_dao, contact_dao, document_dao,
        group_history_dao, academic_course_dao, db, monkeypatch):
        service = StudentService(
            student_dao, contact_dao, document_dao, group_history_dao,
            academic_course_dao, db.transaction,
        )
        student = db.students.create(StudentNew("Jordi", "Garcia", "3r A"))

        def fail_update(_student):
            raise RuntimeError("fallada simulada")

        monkeypatch.setattr(student_dao, "update", fail_update)
        with pytest.raises(RuntimeError, match="fallada simulada"):
            service.change_student_group(
                student.id, "4t A", change_date="2026-01-15"
            )

        assert group_history_dao.get_by_student(student.id) == []
        assert academic_course_dao.get_by_course("2025-2026") is None
        assert student_dao.get_by_id(student.id).group_name == "3r A"
