from typing import Optional
from tutopy.models.messaging import StudentDocument, StudentDocumentNew


class DocumentDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_by_student(self, student_id: int) -> list[StudentDocument]:
        rows = self.conn.execute(
            "SELECT * FROM student_documents WHERE student_id = ? ORDER BY name",
            (student_id,),
        ).fetchall()
        return [StudentDocument(**row) for row in rows]

    def get_by_id(self, id: int) -> Optional[StudentDocument]:
        row = self.conn.execute(
            "SELECT * FROM student_documents WHERE id = ?", (id,)
        ).fetchone()
        return StudentDocument(**row) if row else None

    def get_all(self) -> list[StudentDocument]:
        rows = self.conn.execute(
            "SELECT * FROM student_documents ORDER BY name"
        ).fetchall()
        return [StudentDocument(**row) for row in rows]

    def create(self, data: StudentDocumentNew) -> StudentDocument:
        cur = self.conn.execute(
            "INSERT INTO student_documents "
            "(student_id, name, description, uuid_filename, original_filename, file_path, "
            "date, course_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data.student_id, data.name, data.description,
             data.uuid_filename, data.original_filename, data.file_path,
             data.date, data.course_id),
        )
        self.conn.commit()
        return StudentDocument(
            id=cur.lastrowid, student_id=data.student_id,
            name=data.name, description=data.description,
            uuid_filename=data.uuid_filename,
            original_filename=data.original_filename,
            file_path=data.file_path,
            date=data.date, course_id=data.course_id,
        )

    def update(self, doc: StudentDocument):
        self.conn.execute(
            "UPDATE student_documents SET name=?, description=?, date=?, course_id=? WHERE id=?",
            (doc.name, doc.description, doc.date, doc.course_id, doc.id),
        )
        self.conn.commit()

    def delete(self, id: int):
        self.conn.execute("DELETE FROM student_documents WHERE id = ?", (id,))
        self.conn.commit()
