import uuid as uuid_mod
from typing import Optional
from tutopy.models.messaging import Student, StudentNew
from ._batch import SQLITE_PARAMETER_BATCH


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

    def get_by_ids(self, student_ids: list[int]) -> dict[int, Student]:
        """Retorna els alumnes indicats amb un nombre acotat de consultes."""
        unique_ids = tuple(dict.fromkeys(student_ids))
        students = {}
        for offset in range(0, len(unique_ids), SQLITE_PARAMETER_BATCH):
            batch = unique_ids[offset:offset + SQLITE_PARAMETER_BATCH]
            placeholders = ",".join("?" for _ in batch)
            rows = self.conn.execute(
                "SELECT id, uuid, name, surnames, group_name FROM students "
                f"WHERE id IN ({placeholders})",
                batch,
            )
            students.update((row["id"], Student(**row)) for row in rows)
        return students

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

    def create_with_uuid(self, data: StudentNew, student_uuid: str) -> Student:
        """Crea un alumne conservant una identitat portable validada."""
        cur = self.conn.execute(
            "INSERT INTO students (uuid, name, surnames, group_name) "
            "VALUES (?, ?, ?, ?)",
            (student_uuid, data.name, data.surnames, data.group_name),
        )
        self.conn.commit()
        return Student(
            id=cur.lastrowid, uuid=student_uuid, name=data.name,
            surnames=data.surnames, group_name=data.group_name,
        )

    def update(self, student: Student):
        self.conn.execute(
            "UPDATE students SET name = ?, surnames = ?, group_name = ? WHERE id = ?",
            (student.name, student.surnames, student.group_name, student.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        """Elimina l'alumne; les entitats dependents cauen per claus foranes."""
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
