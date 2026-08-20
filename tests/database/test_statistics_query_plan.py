from tutopy.models.messaging import AcademicCourseNew, StudentNew


def test_estadistiques_per_alumne_i_curs_utilitzen_index_compost(db):
    course = db.academic_courses.create(AcademicCourseNew("2025-2026"))
    db.students.create(StudentNew("Alba", "Serra", "1A"))

    plan = db.conn.execute(
        "EXPLAIN QUERY PLAN "
        "SELECT s.id, COUNT(n.id) FROM students s "
        "LEFT JOIN notes n ON n.student_id = s.id AND n.course_id = ? "
        "WHERE s.group_name = ? GROUP BY s.id",
        (course.id, "1A"),
    ).fetchall()

    details = " ".join(row[3] for row in plan)
    assert "idx_notes_student_course" in details
