from typing import Optional
from tutopy.models.messaging import Note, NoteNew, NoteRecord


def _get_academic_year(date_str: str) -> str:
    parts = date_str.split("-")
    if len(parts) != 3:
        return ""
    try:
        year, month = int(parts[0]), int(parts[1])
    except ValueError:
        return ""
    if month >= 9:
        return f"{year}-{year + 1}"
    return f"{year - 1}-{year}"


class NoteDAO:
    def __init__(self, conn, academic_courses=None):
        self.conn = conn
        self.academic_courses = academic_courses

    def _resolve_course_id(self, date_str: str) -> int:
        """Crea el curs acadèmic si no existieix i, en tot cas, en retorna l'id"""
        year_str = _get_academic_year(date_str)
        if year_str and self.academic_courses:
            return self.academic_courses.get_or_create(year_str).id
        return 0

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
        course_id = data.course_id if data.course_id != 0 else self._resolve_course_id(data.date)
        cur = self.conn.execute(
            "INSERT INTO notes (student_id, category_id, date, course_id, content) "
            "VALUES (?, ?, ?, ?, ?)",
            (data.student_id, data.category_id, data.date, course_id, data.content),
        )
        self.conn.commit()
        return Note(
            id=cur.lastrowid,
            student_id=data.student_id,
            category_id=data.category_id,
            date=data.date,
            course_id=course_id,
            content=data.content,
        )

    def update(self, note: Note):
        course_id = self._resolve_course_id(note.date)
        self.conn.execute(
            "UPDATE notes SET student_id = ?, category_id = ?, date = ?, "
            "course_id = ?, content = ? WHERE id = ?",
            (note.student_id, note.category_id, note.date, course_id, note.content, note.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM notes WHERE id = ?", (id,))
        self.conn.commit()

    def exists(self, student_id: int, category_id: int, date: str, content: str) -> bool:
        row = self.conn.execute(
            "SELECT COUNT(*) FROM notes "
            "WHERE student_id = ? AND category_id = ? AND date = ? AND content = ?",
            (student_id, category_id, date, content),
        ).fetchone()
        return row[0] > 0

    def get_records(self) -> list[NoteRecord]:
        rows = self.conn.execute("""
            SELECT n.id AS note_id, n.date,
                   s.name || ' ' || s.surnames AS student_name,
                   s.group_name,
                   c.name AS category_name, n.content,
                   n.student_id, n.category_id
            FROM notes n
            JOIN students s ON n.student_id = s.id
            JOIN categories c ON n.category_id = c.id
            ORDER BY n.date DESC, n.id DESC
        """).fetchall()
        return [NoteRecord(**row) for row in rows]
