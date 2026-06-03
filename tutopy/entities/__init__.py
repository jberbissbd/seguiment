from dataclasses import dataclass


@dataclass
class Category:
    """Categoria per classificar les notes de seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de la categoria (ex: "Conducta", "Acadèmic").
    """
    id: int
    name: str


@dataclass
class Student:
    """Alumne del qual es fa el seguiment.

    Attributes:
        id: Identificador únic.
        first_name: Nom de l'alumne.
        last_name: Cognom o cognoms de l'alumne.
        group_name: Curs o grup al qual pertany (ex: "2n ESO A").
    """
    id: int
    first_name: str
    last_name: str
    group_name: str

    @property
    def full_name(self) -> str:
        """Retorna el nom complet: ``first_name`` + ``last_name``."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class Note:
    """Nota de seguiment associada a un alumne i una categoria.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
        date: Data en format ISO ``YYYY-MM-DD``.
        content: Contingut textual de la nota.
    """
    id: int
    student_id: int
    category_id: int
    date: str
    content: str


@dataclass
class NoteRecord:
    """Nota amb dades desnormalitzades per a visualització en taula.

    Atributs obtinguts amb un JOIN de les taules ``notes``,
    ``students`` i ``categories``.
    """
    note_id: int
    date: str
    student_name: str
    group_name: str
    category_name: str
    content: str
    student_id: int
    category_id: int
