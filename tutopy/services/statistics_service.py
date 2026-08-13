from datetime import date

from tutopy.models.statistics import StatisticsFilters, StatisticsSnapshot
from tutopy.services.exceptions import ValidationError


class StatisticsService:
    def __init__(self, statistics_dao, courses, categories):
        self.statistics_dao = statistics_dao
        self.courses = courses
        self.categories = categories

    def get_available_courses(self):
        """Retorna només cursos que tenen notes i poden aportar estadístiques."""
        course_ids = self.statistics_dao.get_course_ids_with_notes()
        return tuple(
            course for course_id in course_ids
            if (course := self.courses.get_by_id(course_id)) is not None
        )

    def get_snapshot(self, filters: StatisticsFilters) -> StatisticsSnapshot:
        if not isinstance(filters, StatisticsFilters):
            raise ValidationError("Els filtres estadístics no són vàlids.")
        self._validate_optional_id(filters.course_id, self.courses, "curs acadèmic")
        self._validate_optional_id(filters.category_id, self.categories, "categoria")
        date_from = self._date(filters.date_from)
        date_to = self._date(filters.date_to)
        if date_from and date_to and date_from > date_to:
            raise ValidationError("La data inicial no pot ser posterior a la final.")
        if filters.group_name is not None and (
            not isinstance(filters.group_name, str) or not filters.group_name.strip()
        ):
            raise ValidationError("El grup seleccionat no és vàlid.")
        return self.statistics_dao.get_snapshot(filters)

    @staticmethod
    def _validate_optional_id(value, dao, label):
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"El {label} seleccionat no és vàlid.")
        if dao.get_by_id(value) is None:
            raise ValidationError(f"El {label} seleccionat no existeix.")

    @staticmethod
    def _date(value):
        if value is None:
            return None
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError) as error:
            raise ValidationError("L’interval de dates no és vàlid.") from error
