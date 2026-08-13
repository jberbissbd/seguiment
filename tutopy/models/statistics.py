from dataclasses import dataclass


@dataclass(frozen=True)
class StatisticsFilters:
    course_id: int | None = None
    category_id: int | None = None
    group_name: str | None = None
    date_from: str | None = None
    date_to: str | None = None


@dataclass(frozen=True)
class StatisticValue:
    label: str
    value: int


@dataclass(frozen=True)
class StudentStatistic:
    student_id: int
    student_name: str
    group_name: str
    note_count: int


@dataclass(frozen=True)
class StatisticsSnapshot:
    note_count: int
    student_count: int
    students_with_notes: int
    students_without_notes: int
    average_per_student: float
    by_month: tuple[StatisticValue, ...]
    by_category: tuple[StatisticValue, ...]
    by_student: tuple[StudentStatistic, ...]
