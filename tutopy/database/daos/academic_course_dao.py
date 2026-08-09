from typing import Optional
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew


class AcademicCourseDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_by_id(self, id_course: int) -> Optional[AcademicCourse]:
        row = self.conn.execute(
            "SELECT * FROM academic_courses WHERE id = ?", (id_course,)
        ).fetchone()
        return AcademicCourse(**row) if row else None

    def get_all(self) -> list[AcademicCourse]:
        rows = self.conn.execute(
            "SELECT * FROM academic_courses ORDER BY course DESC"
        ).fetchall()
        return [AcademicCourse(**row) for row in rows]

    def get_by_course(self, course: str) -> Optional[AcademicCourse]:
        row = self.conn.execute(
            "SELECT * FROM academic_courses WHERE course = ?", (course,)
        ).fetchone()
        return AcademicCourse(**row) if row else None

    def create(self, data: AcademicCourseNew) -> AcademicCourse:
        cur = self.conn.execute(
            "INSERT INTO academic_courses (course) VALUES (?)",
            (data.course,),
        )
        self.conn.commit()
        return AcademicCourse(id=cur.lastrowid, course=data.course)

    def get_or_create(self, course: str) -> AcademicCourse:
        existing = self.get_by_course(course)
        if existing:
            return existing
        return self.create(AcademicCourseNew(course=course))

    def update(self, course: AcademicCourse):
        self.conn.execute(
            "UPDATE academic_courses SET course = ? WHERE id = ?",
            (course.course, course.id),
        )
        self.conn.commit()

    def is_deletable(self, id_course: int) -> bool:
        notes = self.conn.execute(
            "SELECT COUNT(*) FROM notes WHERE course_id = ?", (id_course,)
        ).fetchone()[0]
        history = self.conn.execute(
            "SELECT COUNT(*) FROM student_group_history WHERE academic_course_id = ?",
            (id_course,),
        ).fetchone()[0]
        return notes == 0 and history == 0

    def delete(self, id_course: int):
        self.conn.execute("DELETE FROM academic_courses WHERE id = ?", (id_course,))
        self.conn.commit()
