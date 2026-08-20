from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StudentBulkUpdate:
    """Canvis editables d'un alumne dins d'una operació massiva."""

    student_id: int
    name: str
    surnames: str
    group_name: str


@dataclass(frozen=True, slots=True)
class StudentBulkUpdateResult:
    updated: int
    unchanged: int
    group_changes: int
    cancelled: bool = False
