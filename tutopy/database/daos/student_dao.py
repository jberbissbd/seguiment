import uuid as uuid_mod
from typing import Optional
from tutopy.models.messaging import Student, StudentNew


class StudentDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self) -> list[Student]:
        rows = self.conn.execute(
            "SELECT id, uuid, name, surnames, group_name FROM students "
            "ORDER BY surnames, name"
        ).fetchall()
        return [Student(**row) for row in rows]

    def get_by_id(self, id: int) -> Optional[Student]:
        row = self.conn.execute(
            "SELECT id, uuid, name, surnames, group_name FROM students WHERE id = ?",
            (id,),
        ).fetchone()
        return Student(**row) if row else None

    def get_by_uuid(self, uuid: str) -> Optional[Student]:
        row = self.conn.execute(
            "SELECT id, uuid, name, surnames, group_name FROM students WHERE uuid = ?",
            (uuid,),
        ).fetchone()
        return Student(**row) if row else None

    def create(self, data: StudentNew) -> Student:
        """Persisteix un alumne nou i li assigna el seu UUID intern."""
        uid = str(uuid_mod.uuid4())
        cur = self.conn.execute(
            "INSERT INTO students (uuid, name, surnames, group_name) VALUES (?, ?, ?, ?)",
            (uid, data.name, data.surnames, data.group_name),
        )
        self.conn.commit()
        return Student(
            id=cur.lastrowid, uuid=uid,
            name=data.name, surnames=data.surnames,
            group_name=data.group_name,
        )

    def update(self, student: Student):
        self.conn.execute(
            "UPDATE students SET name = ?, surnames = ?, group_name = ? WHERE id = ?",
            (student.name, student.surnames, student.group_name, student.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM notes WHERE student_id = ?", (id,))
        self.conn.execute("DELETE FROM students WHERE id = ?", (id,))
        self.conn.commit()

    def search(self, query: str) -> list[Student]:
        pattern = f"%{query}%"
        rows = self.conn.execute(
            """SELECT id, uuid, name, surnames, group_name FROM students
               WHERE name LIKE ? OR surnames LIKE ?
                  OR (name || ' ' || surnames) LIKE ?
                  OR group_name LIKE ?
               ORDER BY surnames, name""",
            (pattern, pattern, pattern, pattern),
        ).fetchall()
        return [Student(**row) for row in rows]

    def get_groups(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT group_name FROM students "
            "WHERE group_name != '' ORDER BY group_name"
        ).fetchall()
        return [row[0] for row in rows]

    def get_by_full_name(
        self, name: str, surnames: str, group_name: str
    ) -> Optional[Student]:
        row = self.conn.execute(
            "SELECT id, uuid, name, surnames, group_name FROM students "
            "WHERE name = ? AND surnames = ? AND group_name = ?",
            (name, surnames, group_name),
        ).fetchone()
        return Student(**row) if row else None
