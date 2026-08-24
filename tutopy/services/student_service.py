import dataclasses
from datetime import datetime
from typing import Optional, cast
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.contact_dao import ContactDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_group_history_dao import StudentGroupHistoryDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import (
    Student, StudentDetails, StudentNew, StudentGroupHistory,
    StudentGroupHistoryNew,
)
from tutopy.models.student_bulk import StudentBulkUpdate, StudentBulkUpdateResult
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.utils import AcademicCourseDeterminator
from tutopy.services.validation_service import ValidationService



class StudentService:
    def __init__(self, student_dao: StudentDAO, contact_dao: ContactDAO,
        document_dao: DocumentDAO, group_history_dao: StudentGroupHistoryDAO,
        academic_course_dao: AcademicCourseDAO,
        transaction_factory,
        validation_service: ValidationService = None,
        worker_service_factory=None):
        self.student_dao = student_dao
        self.contact_dao = contact_dao
        self.document_dao = document_dao
        self.group_history_dao = group_history_dao
        self.academic_course_dao = academic_course_dao
        self.transaction_factory = transaction_factory
        self.validation_service = validation_service or ValidationService()
        self.worker_service_factory = worker_service_factory

    def get_all(self) -> list[Student]:
        """Retorna tots els alumnes ordenats pel DAO."""
        return self.student_dao.get_all()

    def get_by_id(self, student_id: int) -> Optional[Student]:
        """Retorna un alumne o ``None`` si no existeix."""
        self.validation_service.positive_id(student_id)
        return self.student_dao.get_by_id(student_id)

    def get_by_uuid(self, student_uuid: str) -> Optional[Student]:
        """Retorna un alumne per la seva identitat estable."""
        student_uuid = self.validation_service.required_text(
            student_uuid, "L'UUID de l'alumne no pot estar buit."
        )
        return self.student_dao.get_by_uuid(student_uuid)

    def search(self, query: str) -> list[Student]:
        """Cerca alumnes per nom, cognoms o grup."""
        query = self.validation_service.optional_text(query)
        return self.student_dao.search(query) if query else self.get_all()

    def get_groups(self) -> list[str]:
        """Retorna els grups no buits existents."""
        return self.student_dao.get_groups()

    def create_student(self, student_data: StudentNew) -> Student:
        """Crea l'alumne i registra també el seu grup inicial."""
        with self.transaction_factory():
            student_data = self.validation_service.validate_student(student_data)
            student = self.student_dao.create(student_data)
            if student.group_name:
                self.change_student_group(student.id, student.group_name)
        return student

    def create(self, student_data: StudentNew) -> Student:
        """Àlies CRUD de :meth:`create_student`."""
        return self.create_student(student_data)

    def update(self, student: Student) -> Student:
        """Valida i actualitza un alumne existent, conservant el seu UUID."""
        with self.transaction_factory():
            existing = self._require_student(student.id)
            data = StudentNew(student.name, student.surnames, student.group_name)
            data = self.validation_service.validate_student(data)
            requested_group = data.group_name
            updated = cast(Student, dataclasses.replace(
                existing, name=data.name, surnames=data.surnames
            ))
            self.student_dao.update(updated)
            if requested_group != existing.group_name:
                self.change_student_group(student.id, requested_group)
                updated = cast(
                    Student, dataclasses.replace(updated, group_name=requested_group)
                )
        return updated

    def bulk_update(
        self, changes: list[StudentBulkUpdate], change_date: str,
        progress_callback=None, cancel_requested=None,
    ) -> StudentBulkUpdateResult:
        """Actualitza diversos alumnes atòmicament i conserva l'historial de grup."""
        prepared, change_date = self._validate_bulk_changes(changes, change_date)
        return self._apply_bulk_changes(
            prepared, change_date, progress_callback, cancel_requested
        )

    def _validate_bulk_changes(
        self, changes: list[StudentBulkUpdate], change_date: str
    ) -> tuple[list[tuple[Student, StudentNew]], str]:
        """Valida el lot sencer i retorna els parells (existent, dades noves)."""
        if not isinstance(changes, list) or not changes:
            raise ValidationError("Cal indicar almenys un alumne per actualitzar.")
        identifiers = [self.validation_service.positive_id(item.student_id)
                       for item in changes]
        if len(identifiers) != len(set(identifiers)):
            raise ValidationError("La selecció d’alumnes conté duplicats.")
        change_date = self.validation_service.iso_date(change_date)
        existing_by_id = self.student_dao.get_by_ids(identifiers)
        missing = [item for item in identifiers if item not in existing_by_id]
        if missing:
            raise EntityNotFoundError(
                f"L'alumne amb ID {missing[0]} no existeix."
            )
        prepared = []
        for change in changes:
            data = self.validation_service.validate_student(StudentNew(
                change.name, change.surnames, change.group_name
            ))
            existing = existing_by_id[change.student_id]
            if data.group_name != existing.group_name and not data.group_name:
                raise ValidationError("El grup nou no pot estar buit.")
            prepared.append((existing, data))
        return prepared, change_date

    def _apply_bulk_changes(
        self,
        prepared: list[tuple[Student, StudentNew]],
        change_date: str,
        progress_callback=None,
        cancel_requested=None,
    ) -> StudentBulkUpdateResult:
        """Aplica el lot ja validat dins d'una única transacció, amb cancel·lació."""
        updated = unchanged = group_changes = 0
        try:
            with self.transaction_factory():
                total = len(prepared)
                for completed, (existing, data) in enumerate(prepared, 1):
                    if cancel_requested is not None and cancel_requested():
                        raise _BulkUpdateCancelled
                    changed, group_changed = self._apply_single_bulk_change(
                        existing, data, change_date
                    )
                    if changed:
                        updated += 1
                        group_changes += group_changed
                    else:
                        unchanged += 1
                    if progress_callback is not None:
                        progress_callback(completed, total)
        except _BulkUpdateCancelled:
            return StudentBulkUpdateResult(0, 0, 0, cancelled=True)
        return StudentBulkUpdateResult(updated, unchanged, group_changes)

    def _apply_single_bulk_change(
        self, existing: Student, data: StudentNew, change_date: str
    ) -> tuple[bool, bool]:
        """Aplica un canvi individual i retorna (s'ha actualitzat, ha canviat de grup)."""
        if (
            data.name == existing.name
            and data.surnames == existing.surnames
            and data.group_name == existing.group_name
        ):
            return False, False
        self.student_dao.update(dataclasses.replace(
            existing, name=data.name, surnames=data.surnames
        ))
        group_changed = data.group_name != existing.group_name
        if group_changed:
            self.change_student_group(existing.id, data.group_name, change_date=change_date)
        return True, group_changed

    def bulk_update_with_worker_connection(self, *args, **kwargs):
        """Executa l'edició amb una connexió creada dins del treballador."""
        if self.worker_service_factory is None:
            return self.bulk_update(*args, **kwargs)
        with self.worker_service_factory() as worker_service:
            return worker_service.bulk_update(*args, **kwargs)

    def delete(self, student_id: int) -> None:
        """Elimina un alumne existent i les seves dades dependents."""
        self._require_student(student_id)
        self.student_dao.delete(student_id)

    def get_student_with_contacts(self, student_id: int) -> StudentDetails | None:
        """Obté un alumne amb els seus contactes i documents."""
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            return None
        return StudentDetails(
            student,
            tuple(self.contact_dao.get_by_student(student_id)),
            tuple(self.document_dao.get_by_student(student_id)),
        )

    def get_details(self, student_id: int) -> Optional[StudentDetails]:
        """Retorna l'alumne amb contactes i documents associats."""
        return self.get_student_with_contacts(student_id)

    def get_current_group(self, student_id: int) -> Optional[str]:
        """Obté el grup actual d'un alumne (últim registre amb end_date NULL)."""
        history = self.group_history_dao.get_current(student_id)
        return history.group_name if history else None

    def get_group_history(self, student_id: int) -> list[StudentGroupHistory]:
        """Obté l'històric i repara alumnes antics sense registre inicial."""
        student = self._require_student(student_id)
        history = self.group_history_dao.get_by_student(student_id)
        if not history and student.group_name:
            self.change_student_group(student_id, student.group_name)
            history = self.group_history_dao.get_by_student(student_id)
        return history

    def change_student_group(
        self,
        student_id: int,
        new_group: str,
        academic_course_id: Optional[int] = None,
        change_date: Optional[str] = None
    ) -> StudentGroupHistory:
        """
        Canvia el grup d'un alumne.

        Args:
            student_id: ID de l'alumne.
            new_group: Nom del nou grup (ex: "4t A").
            academic_course_id: ID del curs acadèmic. Si no s'especifica, es resol automàticament.
            change_date: Data del canvi (format YYYY-MM-DD). Si no s'especifica, usa avui.

        Returns:
            StudentGroupHistory: El registre creat.
        """
        with self.transaction_factory():
            change_date = change_date or datetime.now().strftime("%Y-%m-%d")
            student = self._require_student(student_id)
            new_group = self.validation_service.required_text(
                new_group, "El grup no pot estar buit."
            )
            self.validation_service.iso_date(change_date)

            current_history = self.group_history_dao.get_current(student_id)
            if current_history:
                self.group_history_dao.update(
                    dataclasses.replace(current_history, end_date=change_date)
                )

            if academic_course_id is None:
                course_str = AcademicCourseDeterminator().curs_academic_singular(change_date)
                academic_course_id = self.academic_course_dao.get_or_create(course_str).id
            elif not self.academic_course_dao.get_by_id(academic_course_id):
                raise EntityNotFoundError(
                    f"El curs acadèmic amb ID {academic_course_id} no existeix."
                )

            new_history = StudentGroupHistoryNew(
                student_id=student_id,
                group_name=new_group,
                academic_course_id=academic_course_id,
                start_date=change_date,
                end_date=None,
            )
            history = self.group_history_dao.create(new_history)
            self.student_dao.update(
                dataclasses.replace(student, group_name=new_group)
            )
            return history

    def _require_student(self, student_id: int) -> Student:
        self.validation_service.positive_id(student_id)
        student = self.student_dao.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"L'alumne amb ID {student_id} no existeix.")
        return student


class _BulkUpdateCancelled(RuntimeError):
    """Senyal intern que força el rollback de l'edició massiva."""
