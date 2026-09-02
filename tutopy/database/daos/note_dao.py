"""DAO per a les notes de seguiment dels alumnes."""

from typing import Optional
from tutopy.models.messaging import Note, NoteNew, NoteRecord
from ._batch import grouped_by_student
from ._like import like_pattern


class NoteDAO:
    """Accés a persistència per a les notes de seguiment."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[Note]:
        """Retorna les notes d'un alumne, de la més recent a la més antiga."""
        rows = self.conn.execute(
            "SELECT id, student_id, category_id, date, course_id, content "
            "FROM notes WHERE student_id = ? ORDER BY date DESC, id DESC",
            (student_id,),
        ).fetchall()
        return [Note(**row) for row in rows]

    def get_by_students(self, student_ids: list[int]) -> dict[int, list[Note]]:
        """Retorna les anotacions agrupades per alumne en lectures per lots."""
        return grouped_by_student(
            self.conn,
            student_ids,
            "SELECT id, student_id, category_id, date, course_id, content "
            "FROM notes WHERE student_id IN ({placeholders}) "
            "ORDER BY student_id, date DESC, id DESC",
            Note,
        )

    def get_by_id(self, id: int) -> Optional[Note]:
        """Retorna una nota o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, student_id, category_id, date, course_id, content "
            "FROM notes WHERE id = ?",
            (id,),
        ).fetchone()
        return Note(**row) if row else None

    def get_all(self) -> list[Note]:
        """Retorna totes les notes, de la més recent a la més antiga."""
        rows = self.conn.execute(
            "SELECT id, student_id, category_id, date, course_id, content "
            "FROM notes ORDER BY date DESC, id DESC"
        ).fetchall()
        return [Note(**row) for row in rows]

    def create(self, data: NoteNew) -> Note:
        """Crea una nova nota de seguiment."""
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
        """Actualitza una nota existent amb totes les dades noves."""
        self.conn.execute(
            "UPDATE notes SET student_id = ?, category_id = ?, date = ?, "
            "course_id = ?, content = ? WHERE id = ?",
            (note.student_id, note.category_id, note.date, note.course_id, note.content, note.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        """Elimina una nota pel seu identificador."""
        self.conn.execute("DELETE FROM notes WHERE id = ?", (id,))
        self.conn.commit()

    def exists(self, student_id: int, category_id: int, date: str, content: str) -> bool:
        """Indica si ja hi ha una nota idèntica (mateix alumne, categoria, data i contingut).

        Aprofita l'índex ``idx_notes_duplicate_lookup`` per detectar
        duplicats abans d'inserir, per exemple durant una importació massiva.
        """
        row = self.conn.execute(
            "SELECT 1 FROM notes "
            "WHERE student_id = ? AND category_id = ? AND date = ? AND content = ? "
            "LIMIT 1",
            (student_id, category_id, date, content),
        ).fetchone()
        return row is not None

    def get_records(self, filters: dict = None) -> list[NoteRecord]:
        """Retorna registres desnormalitzats aplicant filtres SQL opcionals.

        Args:
            filters: Diccionari amb claus opcionals ``student_id``,
                ``category_id``, ``course_id``, ``date_from``, ``date_to`` i
                ``content`` (cerca parcial, sense distingir majúscules).
                Les claus absents o amb valor ``None`` no filtren.

        Returns:
            Els registres, de la data més recent a la més antiga.
        """
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
            conditions.append("LOWER(n.content) LIKE ? ESCAPE '\\'")
            params.append(like_pattern(filters["content"].lower()))
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
