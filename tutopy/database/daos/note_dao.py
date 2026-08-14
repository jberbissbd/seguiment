from typing import Optional
from tutopy.models.messaging import Note, NoteNew, NoteRecord


class NoteDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[Note]:
        rows = self.conn.execute(
            "SELECT * FROM notes WHERE student_id = ? ORDER BY date DESC, id DESC",
            (student_id,),
        ).fetchall()
        return [Note(**row) for row in rows]

    def get_by_id(self, id: int) -> Optional[Note]:
        row = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?", (id,)
        ).fetchone()
        return Note(**row) if row else None

    def get_all(self) -> list[Note]:
        rows = self.conn.execute(
            "SELECT * FROM notes ORDER BY date DESC, id DESC"
        ).fetchall()
        return [Note(**row) for row in rows]

    def create(self, data: NoteNew) -> Note:
        cur = self.conn.execute(
            "INSERT INTO notes (student_id, category_id, date, course_id, content) "
            "VALUES (?, ?, ?, ?, ?)",
            (data.student_id, data.category_id, data.date, data.course_id, data.content),
        )
        self.conn.commit()
        return Note(
            id=cur.lastrowid,
            student_id=data.student_id,
            category_id=data.category_id,
            date=data.date,
            course_id=data.course_id,
            content=data.content,
        )

    def update(self, note: Note):
        self.conn.execute(
            "UPDATE notes SET student_id = ?, category_id = ?, date = ?, "
            "course_id = ?, content = ? WHERE id = ?",
            (note.student_id, note.category_id, note.date, note.course_id, note.content, note.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM notes WHERE id = ?", (id,))
        self.conn.commit()

    def exists(self, student_id: int, category_id: int, date: str, content: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM notes "
            "WHERE student_id = ? AND category_id = ? AND date = ? AND content = ? "
            "LIMIT 1",
            (student_id, category_id, date, content),
        ).fetchone()
        return row is not None

    def get_records(self, filters: dict = None) -> list[NoteRecord]:
        """Retorna registres desnormalitzats aplicant filtres SQL opcionals."""
        filters = filters or {}
        conditions = []
        params = []
        filter_columns = {
            "student_id": "n.student_id = ?",
            "category_id": "n.category_id = ?",
            "course_id": "n.course_id = ?",
            "date_from": "n.date >= ?",
            "date_to": "n.date <= ?",
        }
        for key, condition in filter_columns.items():
            if filters.get(key) is not None:
                conditions.append(condition)
                params.append(filters[key])
        if filters.get("content"):
            conditions.append("LOWER(n.content) LIKE ?")
            params.append(f"%{filters['content'].lower()}%")
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        query = """
            SELECT n.id AS note_id, n.date,
                   s.name || ' ' || s.surnames AS student_name,
                   s.group_name,
                   c.name AS category_name, n.content,
                   n.student_id, n.category_id
            FROM notes n
            JOIN students s ON n.student_id = s.id
            JOIN categories c ON n.category_id = c.id
        """ + where + " ORDER BY n.date DESC, n.id DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [NoteRecord(**row) for row in rows]
