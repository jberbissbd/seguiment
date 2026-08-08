from tutopy.models.messaging import StudentNew, NoteNew
from tutopy.database.daos.category_dao import CategoryDAO


class ValidationService:
    def __init__(self, category_dao: CategoryDAO):
        self.category_dao = category_dao

    def validate_student(self, student: StudentNew) -> None:
        """Valida les dades d'un alumne nou."""
        if not student.name or not isinstance(student.name, str):
            raise ValueError("El nom de l'alumne no pot estar buit i ha de ser text.")
        if not student.surnames or not isinstance(student.surnames, str):
            raise ValueError("Els cognoms no poden estar buits i han de ser text.")

    def validate_note(self, note: NoteNew) -> None:
        """Valida les dades d'una nota nova."""
        if not note.content or not isinstance(note.content, str):
            raise ValueError("El contingut de la nota no pot estar buit.")
        if not self.category_dao.get_by_id(note.category_id):
            raise ValueError(f"La categoria amb ID {note.category_id} no existeix.")

    def can_delete_category(self, category_id: int) -> bool:
        """Comprova si una categoria es pot eliminar (no té notes associades)."""
        # A NoteDAO hi ha un mètode `exists` que comprova si hi ha notes amb aquesta categoria
        # Podríem afegir un mètode similar a CategoryDAO o usar NoteDAO
        return True  # Implementació pendent