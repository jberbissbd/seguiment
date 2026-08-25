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
    """Alumne del paquet entrant que ja existeix localment amb el mateix UUID.

    Attributes:
        uuid: UUID de l'alumne en conflicte.
        incoming_name: Nom complet de l'alumne al paquet entrant.
        local_name: Nom complet de l'alumne ja existent localment.
    """

    uuid: str
    incoming_name: str
    local_name: str


@dataclass(frozen=True, slots=True)
class TransferDecision:
    """Decisió de l'usuari per a un alumne en conflicte durant la transferència.

    Attributes:
        uuid: UUID de l'alumne al qual s'aplica la decisió.
        action: Acció triada per resoldre el conflicte.
    """

    uuid: str
    action: TransferAction


@dataclass(frozen=True, slots=True)
class TransferPreview:
    """Resum d'un paquet de transferència abans d'importar-lo.

    Attributes:
        source: Fitxer d'origen del paquet.
        student_count: Nombre d'alumnes inclosos al paquet.
        note_count: Nombre de notes incloses al paquet.
        document_count: Nombre de documents inclosos al paquet.
        total_document_bytes: Mida total dels documents, en bytes.
        conflicts: Alumnes que ja existeixen localment amb el mateix UUID.
    """

    source: Path
    student_count: int
    note_count: int
    document_count: int
    total_document_bytes: int
    conflicts: tuple[TransferConflict, ...]


@dataclass(frozen=True, slots=True)
class TransferAnalysisPreparation:
    """Paquet validat criptogràficament pendent de consultar conflictes locals."""

    source: Path
    data: dict


@dataclass(frozen=True, slots=True)
class TransferResult:
    """Recompte del que ha produït la importació d'un paquet de transferència.

    Attributes:
        created: Nombre d'alumnes nous creats.
        replaced: Nombre d'alumnes existents reemplaçats.
        skipped: Nombre d'alumnes en conflicte que s'han mantingut sense canvis.
        imported_as_new: Nombre d'alumnes en conflicte importats com a nous.
        documents: Nombre de documents copiats.
        cancelled: Cert si l'usuari ha cancel·lat l'operació abans d'acabar.
    """

    created: int
    replaced: int
    skipped: int
    imported_as_new: int
    documents: int
    cancelled: bool = False
