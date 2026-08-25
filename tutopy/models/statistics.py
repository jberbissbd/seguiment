"""Models per a les consultes agregades de la pantalla d'estadístiques."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StatisticsFilters:
    """Filtres opcionals aplicables a un càlcul d'estadístiques.

    Attributes:
        course_id: Restringeix a un curs acadèmic.
        category_id: Restringeix a una categoria de notes.
        group_name: Restringeix a un grup d'alumnes.
        date_from: Data mínima (inclosa), en format ``YYYY-MM-DD``.
        date_to: Data màxima (inclosa), en format ``YYYY-MM-DD``.
    """

    course_id: int | None = None
    category_id: int | None = None
    group_name: str | None = None
    date_from: str | None = None
    date_to: str | None = None


@dataclass(frozen=True)
class StatisticValue:
    """Parell etiqueta-valor d'una sèrie agregada (ex: notes per mes).

    Attributes:
        label: Etiqueta de la sèrie (ex: un mes o el nom d'una categoria).
        value: Valor agregat corresponent a l'etiqueta.
    """

    label: str
    value: int


@dataclass(frozen=True)
class StudentStatistic:
    """Recompte de notes d'un alumne dins d'un resum estadístic.

    Attributes:
        student_id: Referència a l'alumne.
        student_name: Nom complet de l'alumne.
        group_name: Grup de l'alumne.
        note_count: Nombre de notes de l'alumne dins dels filtres aplicats.
    """

    student_id: int
    student_name: str
    group_name: str
    note_count: int


@dataclass(frozen=True)
class StatisticsSnapshot:
    """Resum estadístic complet calculat per a uns filtres concrets.

    Attributes:
        note_count: Nombre total de notes dins dels filtres.
        student_count: Nombre total d'alumnes dins dels filtres.
        students_with_notes: Nombre d'alumnes amb almenys una nota.
        students_without_notes: Nombre d'alumnes sense cap nota.
        average_per_student: Mitjana de notes per alumne.
        by_month: Sèrie de recomptes de notes agrupats per mes.
        by_category: Sèrie de recomptes de notes agrupats per categoria.
        by_student: Recompte de notes per alumne.
    """

    note_count: int
    student_count: int
    students_with_notes: int
    students_without_notes: int
    average_per_student: float
    by_month: tuple[StatisticValue, ...]
    by_category: tuple[StatisticValue, ...]
    by_student: tuple[StudentStatistic, ...]
