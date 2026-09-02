"""Mixin compartit per validar l'existència d'un alumne.

Diversos serveis (annotation, contact, document, note, student) necessiten
comprovar que un `student_id` és vàlid i correspon a un alumne existent
abans d'operar-hi. `RequiresStudentMixin` centralitza aquesta comprovació
perquè no calgui duplicar-la a cada servei.
"""

from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import Student
from tutopy.services.exceptions import EntityNotFoundError
from tutopy.services.validation_service import ValidationService


class RequiresStudentMixin:
    """Aporta `_require_student` a serveis amb `student_dao` i `validation_service`."""

    student_dao: StudentDAO
    validation_service: ValidationService

    def _require_student(self, student_id: int) -> Student:
        """Valida l'ID i retorna l'alumne, o llança `EntityNotFoundError`."""
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student
