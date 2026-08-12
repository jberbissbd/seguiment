from dataclasses import dataclass


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
