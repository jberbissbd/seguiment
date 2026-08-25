"""Models per a l'edició massiva d'alumnes."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StudentBulkUpdate:
    """Canvis editables d'un alumne dins d'una operació massiva.

    Attributes:
        student_id: Referència a l'alumne a actualitzar.
        name: Nou nom de l'alumne.
        surnames: Nous cognoms de l'alumne.
        group_name: Nou grup de l'alumne.
    """

    student_id: int
    name: str
    surnames: str
    group_name: str


@dataclass(frozen=True, slots=True)
class StudentBulkUpdateResult:
    """Recompte del que ha produït una edició massiva d'alumnes.

    Attributes:
        updated: Nombre d'alumnes amb algun canvi aplicat.
        unchanged: Nombre d'alumnes sense canvis reals.
        group_changes: Nombre d'alumnes que han canviat de grup.
        cancelled: Cert si l'usuari ha cancel·lat l'operació abans d'acabar.
    """

    updated: int
    unchanged: int
    group_changes: int
    cancelled: bool = False
