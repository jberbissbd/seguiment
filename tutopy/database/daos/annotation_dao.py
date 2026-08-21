from typing import Optional
from tutopy.models.messaging import StudentAnnotation, StudentAnnotationNew
from ._batch import grouped_by_student


class AnnotationDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[StudentAnnotation]:
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
        row = self.conn.execute(
            "SELECT id, student_id, content FROM student_annotations WHERE id = ?",
            (annotation_id,),
        ).fetchone()
        return StudentAnnotation(**row) if row else None

    def create(self, data: StudentAnnotationNew) -> StudentAnnotation:
        cur = self.conn.execute(
            "INSERT INTO student_annotations (student_id, content) VALUES (?, ?)",
            (data.student_id, data.content),
        )
        self.conn.commit()
        return StudentAnnotation(
            id=cur.lastrowid, student_id=data.student_id, content=data.content,
        )

    def update(self, annotation: StudentAnnotation):
        self.conn.execute(
            "UPDATE student_annotations SET content=? WHERE id=?",
            (annotation.content, annotation.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM student_annotations WHERE id = ?", (id,))
        self.conn.commit()
