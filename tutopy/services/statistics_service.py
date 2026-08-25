"""Càlcul d'estadístiques agregades de notes per a la pantalla de resum."""

from datetime import date

from tutopy.models.statistics import (
    StatisticValue, StatisticsFilters, StatisticsSnapshot,
)
from tutopy.services.exceptions import ValidationError


class StatisticsService:
    """Calcula instantànies estadístiques de notes filtrades pel curs i la categoria."""

    MONTH_NAMES = (
        "Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
        "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre",
    )

    def __init__(self, statistics_dao, courses, categories):
        """Rep el DAO d'estadístiques i els repositoris de cursos i categories."""
        self.statistics_dao = statistics_dao
        self.courses = courses
        self.categories = categories

    def get_available_courses(self):
        """Retorna només cursos que tenen notes i poden aportar estadístiques."""
        course_ids = set(self.statistics_dao.get_course_ids_with_notes())
        return tuple(
            course for course in self.courses.get_all() if course.id in course_ids
        )

    def get_snapshot(self, filters: StatisticsFilters) -> StatisticsSnapshot:
        """Valida els filtres i retorna la instantània estadística corresponent.

        Args:
            filters: Filtres de curs, categoria, grup i interval de dates.

        Returns:
            Instantània amb els mesos ja formatats amb nom en català.

        Raises:
            ValidationError: Si algun filtre no és vàlid o l'interval de
                dates és inconsistent.
        """
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
        return self._with_month_labels(self.statistics_dao.get_snapshot(filters))

    @classmethod
    def _with_month_labels(cls, snapshot: StatisticsSnapshot) -> StatisticsSnapshot:
        """Retorna la mateixa instantània amb els mesos etiquetats en català."""
        return StatisticsSnapshot(
            note_count=snapshot.note_count,
            student_count=snapshot.student_count,
            students_with_notes=snapshot.students_with_notes,
            students_without_notes=snapshot.students_without_notes,
            average_per_student=snapshot.average_per_student,
            by_month=tuple(
                StatisticValue(cls._month_label(item.label), item.value)
                for item in snapshot.by_month
            ),
            by_category=snapshot.by_category,
            by_student=snapshot.by_student,
        )

    @classmethod
    def _month_label(cls, value: str) -> str:
        year, month = value.split("-", 1)
        return f"{cls.MONTH_NAMES[int(month) - 1]} {year}"

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
