"""Servei per esborrar totes les dades de l'aplicació de cop."""

from pathlib import Path

from tutopy.database.daos.data_management_dao import DataManagementDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.database.daos.student_photo_dao import PhotoDAO
from tutopy.models.bulk_import import ClearDataResult


class DataManagementService:
    """Esborra totes les dades de la base de dades i els fitxers gestionats associats."""

    def __init__(self, data_dao: DataManagementDAO, documents: DocumentDAO,
                 transaction_factory, storage_dir: str | Path,
                 photo_dao: PhotoDAO = None, photos_storage_dir: str | Path = None):
        """Rep els DAOs de negoci, documents i fotos, i els directoris de magatzem local."""
        self.data_dao = data_dao
        self.documents = documents
        self.transaction_factory = transaction_factory
        self.storage_dir = Path(storage_dir)
        self.photo_dao = photo_dao
        self.photos_storage_dir = Path(photos_storage_dir) if photos_storage_dir else None

    def delete_all(self) -> ClearDataResult:
        """Esborra totes les dades de negoci i els fitxers gestionats del magatzem local.

        Només elimina del disc els fitxers que es trobin directament dins
        dels directoris de magatzem (documents i fotos); els fitxers externs
        es descarten de la base de dades sense tocar-los.

        Returns:
            Nombre de fitxers eliminats i avisos dels que no s'han pogut
            eliminar.
        """
        paths = [Path(document.file_path) for document in self.documents.get_all()
                 if document.file_path]
        photo_paths = [Path(photo.file_path) for photo in self.photo_dao.get_all()
                       if photo.file_path] if self.photo_dao else []
        with self.transaction_factory():
            self.data_dao.delete_all()
        deleted = 0
        warnings = []
        deleted_delta, warnings_delta = self._delete_managed_files(paths, self.storage_dir)
        deleted += deleted_delta
        warnings.extend(warnings_delta)
        if self.photos_storage_dir is not None:
            deleted_delta, warnings_delta = self._delete_managed_files(
                photo_paths, self.photos_storage_dir
            )
            deleted += deleted_delta
            warnings.extend(warnings_delta)
        return ClearDataResult(deleted, tuple(warnings))

    @staticmethod
    def _delete_managed_files(paths: list[Path], storage_dir: Path) -> tuple[int, list[str]]:
        deleted = 0
        warnings = []
        storage = storage_dir.resolve()
        for path in paths:
            try:
                resolved = path.resolve()
                if resolved.parent != storage:
                    continue
                existed = resolved.exists()
                resolved.unlink(missing_ok=True)
                deleted += int(existed)
            except OSError as error:
                warnings.append(f"{path.name}: {error}")
        return deleted, warnings
