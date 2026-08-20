from dataclasses import dataclass

from tutopy.models.messaging import (
    Category,
    Note,
    Student,
    StudentGroupHistory,
)


@dataclass(frozen=True)
class TermConfiguration:
    id: int
    academic_course_id: int
    group_name: str
    second_term_start: str
    third_term_start: str


@dataclass(frozen=True)
class TermConfigurationNew:
    academic_course_id: int
    group_name: str
    second_term_start: str
    third_term_start: str


@dataclass(frozen=True)
class BatchExportFailure:
    student_id: int
    student_name: str
    reason: str


@dataclass(frozen=True)
class BatchExportResult:
    destination: str
    exported: int
    failures: tuple[BatchExportFailure, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportBatchData:
    """Snapshot compartit per generar un o més informes sense consultes N+1."""

    students: dict[int, Student]
    notes: dict[int, list[Note]]
    course_names: dict[int, str]
    categories: tuple[Category, ...]
    histories: dict[int, list[StudentGroupHistory]]
    term_configurations: dict[tuple[int, str], TermConfiguration]
    header_image: str | None
