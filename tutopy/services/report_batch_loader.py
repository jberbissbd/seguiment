from tutopy.models.reporting import ReportBatchData


class ReportBatchLoader:
    """Carrega un snapshot de dades compartides per un lot d'informes."""

    def __init__(self, students, notes, courses, history, configuration):
        self.students = students
        self.notes = notes
        self.courses = courses
        self.history = history
        self.configuration = configuration

    def load(
        self,
        student_ids: list[int],
        *,
        include_histories: bool = False,
        include_terms: bool = False,
        include_header: bool = False,
    ) -> ReportBatchData:
        """Retorna totes les dades requerides amb consultes independents del lot."""
        terms = (
            self.configuration.get_term_configurations() if include_terms else ()
        )
        header = self.configuration.get_header_image() if include_header else None
        return ReportBatchData(
            students=self.students.get_by_ids(student_ids),
            notes=self.notes.get_by_students(student_ids),
            course_names={item.id: item.course for item in self.courses.get_all()},
            categories=tuple(self.configuration.get_ordered_categories()),
            histories=(
                self.history.get_by_students(student_ids)
                if include_histories
                else {student_id: [] for student_id in student_ids}
            ),
            term_configurations={
                (item.academic_course_id, item.group_name): item for item in terms
            },
            header_image=str(header) if header else None,
        )
