"""DAO per als cursos acadèmics."""

from typing import Optional
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew


class AcademicCourseDAO:
    """Accés a persistència per als cursos acadèmics."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_by_id(self, id_course: int) -> Optional[AcademicCourse]:
        """Retorna un curs acadèmic o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, course FROM academic_courses WHERE id = ?", (id_course,)
        ).fetchone()
        return AcademicCourse(**row) if row else None

    def get_all(self) -> list[AcademicCourse]:
        """Retorna tots els cursos acadèmics, ordenats del més recent al més antic."""
        rows = self.conn.execute(
            "SELECT id, course FROM academic_courses ORDER BY course DESC"
        ).fetchall()
        return [AcademicCourse(**row) for row in rows]

    def get_by_course(self, course: str) -> Optional[AcademicCourse]:
        """Retorna el curs acadèmic amb aquest nom, o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, course FROM academic_courses WHERE course = ?", (course,)
        ).fetchone()
        return AcademicCourse(**row) if row else None

    def create(self, data: AcademicCourseNew) -> AcademicCourse:
        """Crea un nou curs acadèmic."""
        cur = self.conn.execute(
            "INSERT INTO academic_courses (course) VALUES (?)",
            (data.course,),
        )
        self.conn.commit()
        return AcademicCourse(id=cur.lastrowid, course=data.course)

    def get_or_create(self, course: str) -> AcademicCourse:
        """Retorna el curs acadèmic existent amb aquest nom, o el crea si no hi és."""
        existing = self.get_by_course(course)
        if existing:
            return existing
        return self.create(AcademicCourseNew(course=course))

    def is_deletable(self, id_course: int) -> bool:
        """Indica si el curs no té notes ni històrics de grup associats."""
        return self.conn.execute(
            "SELECT NOT EXISTS(SELECT 1 FROM notes WHERE course_id = ?) "
            "AND NOT EXISTS(SELECT 1 FROM student_group_history "
            "WHERE academic_course_id = ?)",
            (id_course, id_course),
        ).fetchone()[0] == 1

    def delete(self, id_course: int):
        """Elimina un curs acadèmic pel seu identificador."""
        self.conn.execute("DELETE FROM academic_courses WHERE id = ?", (id_course,))
        self.conn.commit()
