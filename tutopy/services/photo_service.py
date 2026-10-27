"""Servei de gestió de la foto de perfil dels alumnes."""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from tutopy.database.daos.student_photo_dao import PhotoDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.messaging import StudentPhoto
from tutopy.services.exceptions import ValidationError
from tutopy.services._student_requirement import RequiresStudentMixin
from tutopy.services.validation_service import ValidationService


LOGGER = logging.getLogger(__name__)


class PhotoService(RequiresStudentMixin):
    """API de negoci per a la foto de perfil (única, opcional) de cada alumne."""

    def __init__(self, photo_dao: PhotoDAO, student_dao: StudentDAO,
        validation_service: ValidationService = None, storage_dir=None):
        """Injecta els DAOs i el directori de magatzem de fotos gestionades."""
        self.photo_dao = photo_dao
        self.student_dao = student_dao
        self.validation_service = validation_service or ValidationService()
        self.storage_dir = Path(storage_dir) if storage_dir else None

    def get_by_student(self, student_id: int) -> Optional[StudentPhoto]:
        """Retorna la foto d'un alumne, o `None` si no en té."""
        self._require_student(student_id)
        return self.photo_dao.get_by_student(student_id)

    def get_by_students(self, student_ids: list[int]) -> dict[int, Optional[StudentPhoto]]:
        """Carrega la foto de diversos alumnes amb consultes per lots."""
        validated = [self.validation_service.positive_id(item) for item in student_ids]
        return self.photo_dao.get_by_students(validated)

    def set_photo(self, student_id: int, source_path: str) -> StudentPhoto:
        """Valida una imatge i la fixa com a foto de perfil de l'alumne.

        Substitueix i elimina la foto anterior, si n'hi havia una gestionada.

        Args:
            student_id: Identificador de l'alumne.
            source_path: Ruta de la imatge d'origen (jpg, png, etc.).

        Returns:
            La foto desada.

        Raises:
            ValidationError: Si l'alumne no existeix, l'origen no és una
                imatge vàlida, o no s'ha configurat cap magatzem.
        """
        from docx.image.exceptions import UnrecognizedImageError
        from docx.image.image import Image

        self._require_student(student_id)
        if self.storage_dir is None:
            raise ValidationError("No s'ha configurat el directori de fotos.")
        source = Path(source_path)
        if not source.is_file():
            raise ValidationError("El fitxer seleccionat no existeix.")
        try:
            Image.from_file(str(source))
        except (OSError, UnrecognizedImageError) as error:
            raise ValidationError("El fitxer seleccionat no és una imatge vàlida.") from error
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        previous = self.photo_dao.get_by_student(student_id)
        internal_name = f"{uuid.uuid4().hex}{source.suffix.lower()}"
        destination = self.storage_dir / internal_name
        try:
            shutil.copy2(source, destination)
            photo = self.photo_dao.set(StudentPhoto(
                student_id=student_id,
                uuid_filename=internal_name,
                original_filename=source.name,
                file_path=str(destination),
            ))
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        self._delete_managed_file(previous)
        return photo

    def remove_photo(self, student_id: int) -> None:
        """Elimina la foto d'un alumne i el seu fitxer gestionat, de manera segura."""
        self._require_student(student_id)
        photo = self.photo_dao.get_by_student(student_id)
        if photo is None:
            return
        path = Path(photo.file_path) if photo.file_path else None
        quarantined = self._quarantine_photo_file(path)
        try:
            self.photo_dao.delete(student_id)
        except Exception:
            if quarantined is not None:
                self._restore_quarantined_file(quarantined, path, student_id)
            raise
        if quarantined is not None:
            quarantined.unlink(missing_ok=True)

    def get_readable_path(self, student_id: int) -> Optional[Path]:
        """Retorna la ruta de la foto de l'alumne, o `None` si no en té o ha desaparegut."""
        photo = self.get_by_student(student_id)
        return self._readable_path(photo)

    def get_readable_paths(self, student_ids: list[int]) -> dict[int, Optional[Path]]:
        """Retorna la ruta de la foto de diversos alumnes, en lots."""
        photos = self.get_by_students(student_ids)
        return {student_id: self._readable_path(photo) for student_id, photo in photos.items()}

    def _readable_path(self, photo: Optional[StudentPhoto]) -> Optional[Path]:
        if photo is None or self.storage_dir is None or not photo.file_path:
            return None
        try:
            managed = Path(photo.file_path).resolve()
            storage = self.storage_dir.resolve()
        except OSError:
            return None
        if managed.parent != storage or not managed.is_file():
            return None
        return managed

    def _delete_managed_file(self, photo: Optional[StudentPhoto]) -> None:
        if photo is None or not photo.file_path or self.storage_dir is None:
            return
        try:
            managed = Path(photo.file_path).resolve()
            if managed.parent == self.storage_dir.resolve() and managed.is_file():
                managed.unlink(missing_ok=True)
        except OSError:
            LOGGER.warning(
                "No s'ha pogut eliminar la foto anterior: %s", photo.file_path,
                exc_info=True,
            )

    def _quarantine_photo_file(self, path: Optional[Path]) -> Optional[Path]:
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
                "No s'ha pogut preparar la foto per eliminar-la."
            ) from error

    def _restore_quarantined_file(
        self, quarantined: Path, path: Path, student_id: int
    ) -> None:
        """Restaura el fitxer si l'eliminació del registre a la BD ha fallat."""
        try:
            quarantined.replace(path)
        except OSError:
            LOGGER.exception(
                "No s'ha pogut restaurar la foto de l'alumne %s", student_id
            )
