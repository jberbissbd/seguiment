"""Models del protocol portable de transferència entre instàncies."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TransferAction(str, Enum):
    """Decisió aplicable a un alumne amb UUID ja existent."""

    KEEP_LOCAL = "keep_local"
    REPLACE = "replace"
    IMPORT_AS_NEW = "import_as_new"


@dataclass(frozen=True, slots=True)
class TransferConflict:
    uuid: str
    incoming_name: str
    local_name: str


@dataclass(frozen=True, slots=True)
class TransferDecision:
    uuid: str
    action: TransferAction


@dataclass(frozen=True, slots=True)
class TransferPreview:
    source: Path
    student_count: int
    note_count: int
    document_count: int
    total_document_bytes: int
    conflicts: tuple[TransferConflict, ...]


@dataclass(frozen=True, slots=True)
class TransferResult:
    created: int
    replaced: int
    skipped: int
    imported_as_new: int
    documents: int
