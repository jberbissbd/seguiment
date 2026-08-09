import pytest

from tutopy.models.messaging import ContactNew, StudentNew
from tutopy.services.contact_service import ContactService
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


def test_contact_service_crud(contact_dao, student_dao, db):
    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    service = ContactService(contact_dao, student_dao)

    contact = service.create(ContactNew(
        student.id, "  Maria  ", " Mare ", " 600 000 000 ", " correu@example.cat "
    ))
    assert contact.name == "Maria"
    assert service.get_by_student(student.id) == [contact]

    contact.phone = "611 111 111"
    assert service.update(contact).phone == "611 111 111"
    service.delete(contact.id)
    assert service.get_by_student(student.id) == []


def test_contact_service_valida_relacions_i_text(contact_dao, student_dao, db):
    service = ContactService(contact_dao, student_dao)
    with pytest.raises(EntityNotFoundError):
        service.create(ContactNew(999, "Nom", "Relació"))

    student = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    with pytest.raises(ValidationError):
        service.create(ContactNew(student.id, "   ", "Relació"))
