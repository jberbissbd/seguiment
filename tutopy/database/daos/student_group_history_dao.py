from typing import Optional
from tutopy.models.messaging import StudentGroupHistory, StudentGroupHistoryNew


class StudentGroupHistoryDAO:
    """DAO per gestionar l'històric de grups d'alumnes."""

    def __init__(self, conn):
        self.conn = conn

    def create(self, data: StudentGroupHistoryNew) -> StudentGroupHistory:
        """Crea un nou registre d'històric de grup."""
        cur = self.conn.execute(
            """INSERT INTO student_group_history
               (student_id, group_name, academic_course_id, start_date, end_date)
               VALUES (?, ?, ?, ?, ?)""",
            (data.student_id, data.group_name, data.academic_course_id, data.start_date, data.end_date)
        )
        self.conn.commit()
        return StudentGroupHistory(
            id=cur.lastrowid,
            student_id=data.student_id,
            group_name=data.group_name,
            academic_course_id=data.academic_course_id,
            start_date=data.start_date,
            end_date=data.end_date
        )

    def get_by_id(self, id: int) -> Optional[StudentGroupHistory]:
        """Obté un registre d'històric pel seu ID."""
        row = self.conn.execute(
            """SELECT id, student_id, group_name, academic_course_id, start_date, end_date
               FROM student_group_history WHERE id = ?""",
            (id,)
        ).fetchone()
        return StudentGroupHistory(**row) if row else None

    def get_current(self, student_id: int) -> Optional[StudentGroupHistory]:
        """Retorna el grup actual (últim registre amb end_date IS NULL)."""
        row = self.conn.execute(
            """SELECT id, student_id, group_name, academic_course_id, start_date, end_date
               FROM student_group_history
               WHERE student_id = ? AND end_date IS NULL
               ORDER BY start_date DESC LIMIT 1""",
            (student_id,)
        ).fetchone()
        return StudentGroupHistory(**row) if row else None

    def get_by_student(self, student_id: int) -> list[StudentGroupHistory]:
        """Retorna tot l'històric d'un alumne, ordenat per start_date."""
        rows = self.conn.execute(
            """SELECT id, student_id, group_name, academic_course_id, start_date, end_date
               FROM student_group_history
               WHERE student_id = ?
               ORDER BY start_date""",
            (student_id,)
        ).fetchall()
        return [StudentGroupHistory(**row) for row in rows]

    def update(self, history: StudentGroupHistory):
        """Actualitza un registre d'històric (normalment per posar end_date)."""
        self.conn.execute(
            """UPDATE student_group_history
               SET end_date = ?, group_name = ?, academic_course_id = ?
               WHERE id = ?""",
            (history.end_date, history.group_name, history.academic_course_id, history.id)
        )
        self.conn.commit()

    def delete(self, id: int):
        """Elimina un registre d'històric."""
        self.conn.execute(
            "DELETE FROM student_group_history WHERE id = ?",
            (id,)
        )
        self.conn.commit()

    def get_by_course(self, academic_course_id: int) -> list[StudentGroupHistory]:
        """Retorna tots els registres d'un curs acadèmic."""
        rows = self.conn.execute(
            """SELECT id, student_id, group_name, academic_course_id, start_date, end_date
               FROM student_group_history
               WHERE academic_course_id = ?
               ORDER BY start_date""",
            (academic_course_id,)
        ).fetchall()
        return [StudentGroupHistory(**row) for row in rows]

    def get_by_course_and_date(self, academic_course_id: int, date: str) -> list[StudentGroupHistory]:
        """Retorna els grups actius en una data concreta d'un curs."""
        rows = self.conn.execute(
            """SELECT id, student_id, group_name, academic_course_id, start_date, end_date
               FROM student_group_history
               WHERE academic_course_id = ?
                 AND start_date <= ?
                 AND (end_date IS NULL OR end_date >= ?)
               ORDER BY start_date""",
            (academic_course_id, date, date)
        ).fetchall()
        return [StudentGroupHistory(**row) for row in rows]
