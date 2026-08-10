from dataclasses import dataclass, field
from enum import Enum

from tutopy.models.messaging import Student


@dataclass(frozen=True)
class ImportIssue:
    sheet: str
    row: int
    reason: str

    def __str__(self) -> str:
        return f"{self.sheet} — fila {self.row}: {self.reason}"


@dataclass(frozen=True)
class StudentImportRow:
    row: int
    name: str
    surnames: str
    group_name: str

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surnames}".strip()


@dataclass(frozen=True)
class CategoryImportRow:
    row: int
    name: str


@dataclass(frozen=True)
class StudentConflict:
    row: StudentImportRow
    matches: tuple[Student, ...]


@dataclass(frozen=True)
class ImportPreview:
    students: tuple[StudentImportRow, ...] = ()
    categories: tuple[CategoryImportRow, ...] = ()
    conflicts: tuple[StudentConflict, ...] = ()
    issues: tuple[ImportIssue, ...] = ()


class ImportAction(str, Enum):
    CREATE = "create"
    SKIP = "skip"
    UPDATE = "update"


@dataclass(frozen=True)
class ImportDecision:
    row: int
    action: ImportAction
    student_id: int | None = None


@dataclass(frozen=True)
class ImportResult:
    students_created: int = 0
    students_updated: int = 0
    students_skipped: int = 0
    categories_created: int = 0
    categories_reused: int = 0


@dataclass(frozen=True)
class ClearDataResult:
    deleted_files: int = 0
    file_warnings: tuple[str, ...] = field(default_factory=tuple)
