"""Models per a la importació massiva d'alumnes i categories des de fulls de càlcul."""

from dataclasses import dataclass, field
from enum import Enum

from tutopy.models.messaging import Student


@dataclass(frozen=True)
class ImportIssue:
    """Problema detectat en una fila d'un full durant la importació.

    Attributes:
        sheet: Nom del full on s'ha detectat el problema.
        row: Número de fila (dins del full) afectada.
        reason: Descripció llegible del problema.
    """

    sheet: str
    row: int
    reason: str

    def __str__(self) -> str:
        """Retorna una descripció llegible: full, fila i motiu."""
        return f"{self.sheet} — fila {self.row}: {self.reason}"


@dataclass(frozen=True)
class StudentImportRow:
    """Fila d'alumne llegida d'un full d'importació, pendent de decisió.

    Attributes:
        row: Número de fila dins del full.
        name: Nom de l'alumne tal com apareix al full.
        surnames: Cognoms de l'alumne tal com apareixen al full.
        group_name: Grup al qual s'assignarà l'alumne.
    """

    row: int
    name: str
    surnames: str
    group_name: str

    @property
    def full_name(self) -> str:
        """Retorna el nom complet: ``name`` + ``surnames``."""
        return f"{self.name} {self.surnames}".strip()


@dataclass(frozen=True)
class CategoryImportRow:
    """Fila de categoria llegida d'un full d'importació.

    Attributes:
        row: Número de fila dins del full.
        name: Nom de la categoria tal com apareix al full.
    """

    row: int
    name: str


@dataclass(frozen=True)
class StudentConflict:
    """Fila d'alumne que coincideix amb un o més alumnes ja existents.

    Attributes:
        row: Fila d'importació en conflicte.
        matches: Alumnes existents que coincideixen amb la fila.
    """

    row: StudentImportRow
    matches: tuple[Student, ...]


@dataclass(frozen=True)
class ImportPreview:
    """Resultat de l'anàlisi d'un full abans d'aplicar cap canvi.

    Attributes:
        students: Files d'alumnes detectades.
        categories: Files de categories detectades.
        conflicts: Files d'alumnes que coincideixen amb alumnes existents.
        issues: Problemes detectats que impedeixen importar certes files.
    """

    students: tuple[StudentImportRow, ...] = ()
    categories: tuple[CategoryImportRow, ...] = ()
    conflicts: tuple[StudentConflict, ...] = ()
    issues: tuple[ImportIssue, ...] = ()


class ImportAction(str, Enum):
    """Decisió aplicable a una fila d'alumne en conflicte durant la importació."""

    CREATE = "create"
    SKIP = "skip"
    UPDATE = "update"


@dataclass(frozen=True)
class ImportDecision:
    """Decisió de l'usuari per a una fila concreta de la importació.

    Attributes:
        row: Número de fila a la qual s'aplica la decisió.
        action: Acció triada per a la fila.
        student_id: Alumne existent afectat quan l'acció és `UPDATE`.
    """

    row: int
    action: ImportAction
    student_id: int | None = None


@dataclass(frozen=True)
class ImportResult:
    """Recompte del que ha produït una importació massiva.

    Attributes:
        students_created: Nombre d'alumnes nous creats.
        students_updated: Nombre d'alumnes existents actualitzats.
        students_skipped: Nombre de files d'alumnes ometudes.
        categories_created: Nombre de categories noves creades.
        categories_reused: Nombre de categories existents reutilitzades.
    """

    students_created: int = 0
    students_updated: int = 0
    students_skipped: int = 0
    categories_created: int = 0
    categories_reused: int = 0


@dataclass(frozen=True)
class ClearDataResult:
    """Resultat d'esborrar totes les dades de l'aplicació.

    Attributes:
        deleted_files: Nombre de fitxers de documents eliminats del disc.
        file_warnings: Avisos per a fitxers que no s'han pogut eliminar.
    """

    deleted_files: int = 0
    file_warnings: tuple[str, ...] = field(default_factory=tuple)
