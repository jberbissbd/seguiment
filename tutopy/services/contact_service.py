"""Servei de gestió dels contactes associats als alumnes."""

import dataclasses
from typing import cast

from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import Contact, ContactNew
from tutopy.services.exceptions import EntityNotFoundError
from tutopy.services.validation_service import ValidationService


class ContactService:
    """API de negoci per als contactes associats a alumnes."""

    def __init__(self, contact_dao: ContactDAO, student_dao: StudentDAO,
        validation_service: ValidationService = None):
        """Rep el DAO de contactes, el d'alumnes i el servei de validació."""
        self.contact_dao = contact_dao
        self.student_dao = student_dao
        self.validation_service = validation_service or ValidationService()

    def get_by_student(self, student_id: int) -> list[Contact]:
        """Retorna els contactes d'un alumne existent."""
        self._require_student(student_id)
        return self.contact_dao.get_by_student(student_id)

    def get_by_id(self, contact_id: int) -> Contact:
        """Retorna un contacte pel seu ID."""
        self.validation_service.positive_id(contact_id)
        contact = self.contact_dao.get_by_id(contact_id)
        if contact is None:
            raise EntityNotFoundError(f"El contacte amb ID {contact_id} no existeix.")
        return contact

    def create(self, data: ContactNew) -> Contact:
        """Valida i crea un nou contacte per a un alumne existent."""
        self._require_student(data.student_id)
        prepared = self._prepare(data)
        return self.contact_dao.create(prepared)

    def update(self, contact: Contact) -> Contact:
        """Valida i actualitza les dades d'un contacte existent."""
        existing = self.get_by_id(contact.id)
        prepared = self._prepare(ContactNew(
            existing.student_id, contact.name, contact.description,
            contact.phone, contact.email,
        ))
        updated = cast(Contact, dataclasses.replace(
            existing, name=prepared.name, description=prepared.description,
            phone=prepared.phone, email=prepared.email,
        ))
        self.contact_dao.update(updated)
        return updated

    def delete(self, contact_id: int) -> None:
        """Elimina un contacte pel seu ID."""
        self.get_by_id(contact_id)
        self.contact_dao.delete(contact_id)

    def _prepare(self, data: ContactNew) -> ContactNew:
        return ContactNew(
            student_id=data.student_id,
            name=self.validation_service.required_text(
                data.name, "El nom del contacte no pot estar buit."
            ),
            description=self.validation_service.required_text(
                data.description, "La descripció del contacte no pot estar buida."
            ),
            phone=self.validation_service.optional_text(data.phone),
            email=self.validation_service.optional_text(data.email),
        )

    def _require_student(self, student_id: int):
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
