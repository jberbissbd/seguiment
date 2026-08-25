"""DAO per a consultes agregades de seguiment usades a les estadístiques."""

from tutopy.models.statistics import (
    StatisticValue, StatisticsFilters, StatisticsSnapshot, StudentStatistic,
)


class StatisticsDAO:
    """Consultes agregades de seguiment; no carrega el text de les notes."""

    AND = " AND "

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_course_ids_with_notes(self) -> tuple[int, ...]:
        """Retorna els identificadors de curs que tenen alguna nota, del més recent al més antic."""
        rows = self.conn.execute(
            "SELECT DISTINCT n.course_id FROM notes n "
            "JOIN academic_courses c ON c.id = n.course_id "
            "ORDER BY c.course DESC"
        ).fetchall()
        return tuple(row[0] for row in rows)

    def get_snapshot(self, filters: StatisticsFilters) -> StatisticsSnapshot:
        """Calcula un resum estadístic filtrat sense carregar el text de les notes.

        Totes les agregacions (recomptes, agrupacions per mes/categoria i per
        alumne) es fan amb SQL, de manera que el cost és ``O(N + S)`` i no
        creix amb la mida del contingut de les notes.

        Args:
            filters: Filtres opcionals de curs, categoria, grup i rang de
                dates a aplicar.

        Returns:
            Un `StatisticsSnapshot` amb els recomptes i les sèries agregades.
        """
        note_where, note_params = self._note_filters(filters)
        student_where, student_params = self._student_filters(filters)

        student_count = self.conn.execute(
            "SELECT COUNT(*) FROM students s" + student_where, student_params
        ).fetchone()[0]
        note_summary = self.conn.execute(
            "SELECT COUNT(*) AS note_count, COUNT(DISTINCT n.student_id) AS covered "
            "FROM notes n JOIN students s ON s.id = n.student_id" + note_where,
            note_params,
        ).fetchone()
        note_count = note_summary["note_count"]
        covered = note_summary["covered"]

        by_month = self._values(
            "SELECT substr(n.date, 1, 7) AS label, COUNT(*) AS value "
            "FROM notes n JOIN students s ON s.id = n.student_id" + note_where
            + " GROUP BY substr(n.date, 1, 7) ORDER BY label",
            note_params,
        )
        by_category = self._values(
            "SELECT c.name AS label, COUNT(*) AS value "
            "FROM notes n JOIN students s ON s.id = n.student_id "
            "JOIN categories c ON c.id = n.category_id" + note_where
            + " GROUP BY c.id, c.name ORDER BY value DESC, c.name",
            note_params,
        )

        # Els filtres de notes van a l'ON per conservar alumnes amb recompte zero.
        join_conditions, join_params = self._note_conditions(filters, include_group=False)
        on = self.AND + self.AND.join(join_conditions) if join_conditions else ""
        rows = self.conn.execute(
            "SELECT s.id AS student_id, s.surnames || ', ' || s.name AS student_name, "
            "s.group_name, COUNT(n.id) AS note_count FROM students s "
            "LEFT JOIN notes n ON n.student_id = s.id" + on + student_where
            + " GROUP BY s.id, s.name, s.surnames, s.group_name "
              "ORDER BY note_count DESC, s.surnames, s.name",
            [*join_params, *student_params],
        ).fetchall()
        by_student = tuple(StudentStatistic(**row) for row in rows)
        return StatisticsSnapshot(
            note_count=note_count,
            student_count=student_count,
            students_with_notes=covered,
            students_without_notes=max(0, student_count - covered),
            average_per_student=(note_count / student_count if student_count else 0.0),
            by_month=by_month,
            by_category=by_category,
            by_student=by_student,
        )

    def _values(self, query, params):
        return tuple(StatisticValue(**row) for row in self.conn.execute(query, params))

    def _note_filters(self, filters):
        conditions, params = self._note_conditions(filters, include_group=True)
        return (" WHERE " + self.AND.join(conditions) if conditions else "", params)

    @staticmethod
    def _note_conditions(filters, include_group):
        conditions = []
        params = []
        for value, expression in (
            (filters.course_id, "n.course_id = ?"),
            (filters.category_id, "n.category_id = ?"),
            (filters.date_from, "n.date >= ?"),
            (filters.date_to, "n.date <= ?"),
        ):
            if value is not None:
                conditions.append(expression)
                params.append(value)
        if include_group and filters.group_name is not None:
            conditions.append("s.group_name = ?")
            params.append(filters.group_name)
        return conditions, params

    @staticmethod
    def _student_filters(filters):
        if filters.group_name is None:
            return "", []
        return " WHERE s.group_name = ?", [filters.group_name]
