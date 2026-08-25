"""DAO per als descriptors generals (no datats) d'alumnes."""

from typing import Optional
from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew
from ._batch import grouped_by_student


class AnnotationDAO:
    """Accés a persistència per als descriptors generals d'alumnes."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[StudentAnnotation]:
        """Retorna els descriptors d'un alumne."""
        rows = self.conn.execute(
            "SELECT id, student_id, content FROM student_annotations "
            "WHERE student_id = ? ORDER BY id",
            (student_id,),
        ).fetchall()
        return [StudentAnnotation(**row) for row in rows]

    def get_by_students(
        self, student_ids: list[int]
    ) -> dict[int, list[StudentAnnotation]]:
        """Retorna els descriptors agrupats per alumne en lectures per lots."""
        return grouped_by_student(
            self.conn,
            student_ids,
            "SELECT id, student_id, content FROM student_annotations "
            "WHERE student_id IN ({placeholders}) ORDER BY student_id, id",
            StudentAnnotation,
        )

    def get_by_id(self, annotation_id: int) -> Optional[StudentAnnotation]:
        """Retorna un descriptor o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, student_id, content FROM student_annotations WHERE id = ?",
            (annotation_id,),
        ).fetchone()
        return StudentAnnotation(**row) if row else None

    def create(self, data: StudentAnnotationNew) -> StudentAnnotation:
        """Crea un nou descriptor per a un alumne."""
        cur = self.conn.execute(
            "INSERT INTO student_annotations (student_id, content) VALUES (?, ?)",
            (data.student_id, data.content),
        )
        self.conn.commit()
        return StudentAnnotation(
            id=cur.lastrowid, student_id=data.student_id, content=data.content,
        )

    def update(self, annotation: StudentAnnotation):
        """Actualitza el contingut d'un descriptor existent."""
        self.conn.execute(
            "UPDATE student_annotations SET content=? WHERE id=?",
            (annotation.content, annotation.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        """Elimina un descriptor pel seu identificador."""
        self.conn.execute("DELETE FROM student_annotations WHERE id = ?", (id,))
        self.conn.commit()
