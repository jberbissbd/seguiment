import datetime
import re

from tutopy.models.messaging import StudentNew, NoteNew
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


ACADEMIC_COURSE_PATTERN = re.compile(r"^(\d{4})-(\d{4})$")


class ValidationService:
    def __init__(self, category_dao: CategoryDAO = None):
        self.category_dao = category_dao

    def validate_student(self, student: StudentNew) -> None:
        """Valida i normalitza les dades d'un alumne nou."""
        student.name = self.person_name(
            student.name, "El nom de l'alumne no pot estar buit i ha de ser text."
        )
        student.surnames = self.person_name(
            student.surnames, "Els cognoms no poden estar buits i han de ser text."
        )
        student.group_name = self.optional_text(student.group_name)

    def validate_note(self, note: NoteNew) -> None:
        """Valida i normalitza les dades d'una nota nova."""
        note.content = self.required_text(
            note.content, "El contingut de la nota no pot estar buit."
        )
        self.iso_date(note.date)
        self.positive_id(note.student_id, "L'identificador de l'alumne no és vàlid.")
        self.positive_id(note.category_id, "L'identificador de la categoria no és vàlid.")
        if note.course_id < 0:
            raise ValidationError("L'identificador del curs acadèmic no és vàlid.")
        if self.category_dao is None:
            raise RuntimeError("Cal un CategoryDAO per validar notes.")
        if not self.category_dao.get_by_id(note.category_id):
            raise EntityNotFoundError(
                f"La categoria amb ID {note.category_id} no existeix."
            )

    def can_delete_category(self, category_id: int) -> bool:
        """Comprova si una categoria es pot eliminar (no té notes associades)."""
        if self.category_dao.is_deletable(category_id):
            return True
        return False

    @staticmethod
    def required_text(value: str, message: str) -> str:
        """Retorna un text normalitzat o genera un error de validació."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(message)
        return value.strip()

    @staticmethod
    def person_name(value: str, message: str) -> str:
        """Normalitza espais d'un nom conservant-ne l'ortografia original.

        Elimina espais exteriors i converteix qualsevol seqüència d'espais,
        tabulacions o salts de línia en un únic espai. No altera majúscules,
        accents, apòstrofs ni guionets.
        """
        value = ValidationService.required_text(value, message)
        return " ".join(value.split())

    @staticmethod
    def optional_text(value: str, message: str = "El valor ha de ser text.") -> str:
        """Normalitza un text opcional."""
        if not isinstance(value, str):
            raise ValidationError(message)
        return value.strip()

    @staticmethod
    def positive_id(value: int, message: str = "L'identificador no és vàlid.") -> int:
        """Valida un identificador enter estrictament positiu."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(message)
        return value

    @staticmethod
    def iso_date(value: str, message: str = "La data ha de tenir el format YYYY-MM-DD.") -> str:
        """Valida una data ISO real, no només la seva forma textual."""
        if not isinstance(value, str):
            raise ValidationError(message)
        try:
            datetime.date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError(message) from exc
        return value

    @staticmethod
    def academic_course(value: str) -> str:
        """Valida i normalitza un curs en format YYYY-YYYY consecutiu."""
        value = ValidationService.required_text(
            value, "El curs acadèmic no pot estar buit."
        )
        match = ACADEMIC_COURSE_PATTERN.fullmatch(value)
        if not match or int(match.group(2)) != int(match.group(1)) + 1:
            raise ValidationError(
                "El curs acadèmic ha de tenir el format YYYY-YYYY amb anys consecutius."
            )
        return value
