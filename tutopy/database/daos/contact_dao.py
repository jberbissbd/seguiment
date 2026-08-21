from typing import Optional
from tutopy.models.messaging import Contact, ContactNew
from ._batch import grouped_by_student


class ContactDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[Contact]:
        rows = self.conn.execute(
            "SELECT id, student_id, name, description, phone, email FROM contacts "
            "WHERE student_id = ? ORDER BY name",
            (student_id,),
        ).fetchall()
        return [Contact(**row) for row in rows]

    def get_by_students(self, student_ids: list[int]) -> dict[int, list[Contact]]:
        """Retorna els contactes agrupats per alumne en lectures per lots."""
        return grouped_by_student(
            self.conn,
            student_ids,
            "SELECT id, student_id, name, description, phone, email FROM contacts "
            "WHERE student_id IN ({placeholders}) ORDER BY student_id, name",
            Contact,
        )

    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        row = self.conn.execute(
            "SELECT id, student_id, name, description, phone, email "
            "FROM contacts WHERE id = ?",
            (contact_id,),
        ).fetchone()
        return Contact(**row) if row else None

    def create(self, data: ContactNew) -> Contact:
        cur = self.conn.execute(
            "INSERT INTO contacts (student_id, name, description, phone, email) "
            "VALUES (?, ?, ?, ?, ?)",
            (data.student_id, data.name, data.description, data.phone, data.email),
        )
        self.conn.commit()
        return Contact(
            id=cur.lastrowid, student_id=data.student_id,
            name=data.name, description=data.description,
            phone=data.phone, email=data.email,
        )

    def update(self, contact: Contact):
        self.conn.execute(
            "UPDATE contacts SET name=?, description=?, phone=?, email=? WHERE id=?",
            (contact.name, contact.description, contact.phone, contact.email, contact.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM contacts WHERE id = ?", (id,))
        self.conn.commit()
