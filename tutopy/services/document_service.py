"""Servei de gestió de documents d'alumnes: metadades i fitxers gestionats."""

import dataclasses
import logging
import shutil
import uuid
from pathlib import Path
from typing import cast

from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.database.daos.academic_course_dao import AcademicCourseDAO
from tutopy.models.messaging import StudentDocument, StudentDocumentNew
from tutopy.services.exceptions import (
    EntityNotFoundError,
    FileCleanupError,
    ValidationError,
)
from tutopy.services.validation_service import ValidationService
from tutopy.services._student_requirement import RequiresStudentMixin
from tutopy.services.utils import AcademicCourseDeterminator


LOGGER = logging.getLogger(__name__)


class DocumentService(RequiresStudentMixin):
    """API de negoci per a les metadades dels documents d'alumnes."""

    def __init__(self, document_dao: DocumentDAO, student_dao: StudentDAO,
        academic_course_dao: AcademicCourseDAO = None,
        validation_service: ValidationService = None, storage_dir=None):
        """Injecta els DAOs i el directori de magatzem de fitxers gestionats."""
        self.document_dao = document_dao
        self.student_dao = student_dao
        self.academic_course_dao = academic_course_dao
        self.validation_service = validation_service or ValidationService()
        self.storage_dir = Path(storage_dir) if storage_dir else None

    def get_all(self) -> list[StudentDocument]:
        """Retorna tots els documents registrats."""
        return self.document_dao.get_all()

    def get_by_student(self, student_id: int) -> list[StudentDocument]:
        """Retorna els documents d'un alumne existent."""
        self._require_student(student_id)
        return self.document_dao.get_by_student(student_id)

    def get_by_students(
        self, student_ids: list[int]
    ) -> dict[int, list[StudentDocument]]:
        """Carrega els documents de diversos alumnes amb consultes per lots."""
        validated = [self.validation_service.positive_id(item) for item in student_ids]
        existing = self.student_dao.get_by_ids(validated)
        missing = [item for item in validated if item not in existing]
        if missing:
            raise EntityNotFoundError(
                f"L'alumne amb ID {missing[0]} no existeix."
            )
        return self.document_dao.get_by_students(validated)

    def get_by_id(self, document_id: int) -> StudentDocument:
        """Retorna un document pel seu ID o llança `EntityNotFoundError`."""
        self.validation_service.positive_id(document_id)
        document = self.document_dao.get_by_id(document_id)
        if document is None:
            raise EntityNotFoundError(f"El document amb ID {document_id} no existeix.")
        return document

    def create(self, data: StudentDocumentNew) -> StudentDocument:
        """Valida i registra les metadades d'un nou document per a un alumne."""
        self._require_student(data.student_id)
        return self.document_dao.create(self._prepare(data))

    def import_file(self, student_id: int, name: str, description: str,
        source_path: str, date: str = "") -> StudentDocument:
        """Copia un fitxer al magatzem gestionat i en desa les metadades."""
        self._require_student(student_id)
        if self.storage_dir is None:
            raise ValidationError("No s'ha configurat el directori de documents.")
        source = Path(source_path)
        if not source.is_file():
            raise ValidationError("El fitxer seleccionat no existeix.")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        internal_name = f"{uuid.uuid4()}{source.suffix.lower()}"
        destination = self.storage_dir / internal_name
        try:
            shutil.copy2(source, destination)
            return self.create(StudentDocumentNew(
                student_id=student_id,
                name=name,
                description=description,
                uuid_filename=internal_name,
                original_filename=source.name,
                file_path=str(destination),
                date=date,
            ))
        # La neteja s'ha d'executar davant qualsevol fallada posterior a la
        # còpia (inclòs un defecte inesperat); l'excepció original es conserva.
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def update(self, document: StudentDocument) -> StudentDocument:
        """Actualitza les metadades d'un document, conservant el fitxer gestionat."""
        existing = self.get_by_id(document.id)
        prepared = self._prepare(StudentDocumentNew(
            student_id=existing.student_id,
            name=document.name,
            description=document.description,
            uuid_filename=existing.uuid_filename,
            original_filename=existing.original_filename,
            file_path=existing.file_path,
            date=document.date,
            course_id=document.course_id,
        ))
        updated = cast(StudentDocument, dataclasses.replace(
            existing, name=prepared.name, description=prepared.description,
            date=prepared.date, course_id=prepared.course_id,
        ))
        self.document_dao.update(updated)
        return updated

    def get_readable_path(self, document_id: int) -> Path:
        """Retorna el fitxer gestionat després de validar-ne ubicació i existència."""
        return self.get_readable_document_path(self.get_by_id(document_id))

    def get_readable_document_path(self, document: StudentDocument) -> Path:
        """Valida la ruta d'un document que ja s'ha carregat de persistència."""
        if self.storage_dir is None or not document.file_path:
            raise ValidationError("El document no té cap fitxer gestionat.")
        path = Path(document.file_path)
        try:
            managed = path.resolve()
            storage = self.storage_dir.resolve()
        except OSError as error:
            raise ValidationError("No s'ha pogut localitzar el document.") from error
        if managed.parent != storage or not managed.is_file():
            raise ValidationError("El fitxer del document no existeix o no és accessible.")
        return managed

    def export_file(self, document_id: int, destination_path: str) -> Path:
        """Copia un document gestionat a una ubicació escollida per l'usuari."""
        return self.export_document(self.get_by_id(document_id), destination_path)

    def export_document(
        self, document: StudentDocument, destination_path: str
    ) -> Path:
        """Copia un document ja carregat sense tornar-ne a consultar les metadades."""
        source = self.get_readable_document_path(document)
        destination = Path(destination_path)
        if not destination.name:
            raise ValidationError("Cal indicar una destinació per exportar el document.")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source == destination.resolve():
                raise ValidationError("El document ja es troba en aquesta ubicació.")
            shutil.copy2(source, destination)
        except ValidationError:
            raise
        except OSError as error:
            raise ValidationError("No s'ha pogut exportar el document.") from error
        return destination

    def delete(self, document_id: int) -> StudentDocument:
        """Elimina un document i el seu fitxer gestionat, amb neteja transaccional."""
        document = self.get_by_id(document_id)
        path = Path(document.file_path) if document.file_path else None
        quarantined = self._quarantine_document_file(path)
        try:
            self.document_dao.delete(document_id)
        except Exception:
            if quarantined is not None:
                self._restore_quarantined_file(quarantined, path, document_id)
            raise
        if quarantined is not None:
            self._finalize_quarantine(quarantined)
        return document

    def _quarantine_document_file(self, path: Path | None) -> Path | None:
        """Mou el fitxer gestionat a un nom temporal abans d'esborrar-ne el registre."""
        if not path or not self.storage_dir:
            return None
        try:
            managed = path.resolve()
            if managed.parent != self.storage_dir.resolve() or not managed.is_file():
                return None
            quarantined = managed.with_name(
                f".{managed.name}.{uuid.uuid4().hex}.deleting"
            )
            managed.replace(quarantined)
            return quarantined
        except OSError as error:
            raise ValidationError(
                "No s'ha pogut preparar el fitxer del document per eliminar-lo."
            ) from error

    def _restore_quarantined_file(
        self, quarantined: Path, path: Path, document_id: int
    ) -> None:
        """Restaura el fitxer si l'eliminació del registre a la BD ha fallat."""
        try:
            quarantined.replace(path)
        except OSError:
            LOGGER.exception(
                "No s'ha pogut restaurar el fitxer del document %s", document_id
            )

    def _finalize_quarantine(self, quarantined: Path) -> None:
        """Esborra definitivament el fitxer un cop confirmada l'eliminació a la BD."""
        try:
            quarantined.unlink()
        except OSError as error:
            raise FileCleanupError(
                "El document s'ha eliminat, però no s'ha pogut esborrar "
                "completament el fitxer associat."
            ) from error

    def _prepare(self, data: StudentDocumentNew) -> StudentDocumentNew:
        if not data.date:
            raise ValidationError("La data del document és obligatòria.")
        document_date = self.validation_service.iso_date(data.date)
        course_id = data.course_id
        if document_date:
            if self.academic_course_dao is None:
                raise ValidationError("No es pot determinar el curs acadèmic del document.")
            course_name = AcademicCourseDeterminator().curs_academic_singular(document_date)
            course_id = self.academic_course_dao.get_or_create(course_name).id
        return StudentDocumentNew(
            student_id=data.student_id,
            name=self.validation_service.required_text(
                data.name, "El nom del document no pot estar buit."
            ),
            description=self.validation_service.optional_text(data.description),
            uuid_filename=self.validation_service.required_text(
                data.uuid_filename, "El nom intern del document no pot estar buit."
            ),
            original_filename=self.validation_service.optional_text(data.original_filename),
            file_path=self.validation_service.optional_text(data.file_path),
            date=document_date,
            course_id=course_id,
        )
