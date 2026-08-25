"""Servei per esborrar totes les dades de l'aplicació de cop."""

from pathlib import Path

from tutopy.database.daos.data_management_dao import DataManagementDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.models.bulk_import import ClearDataResult


class DataManagementService:
    """Esborra totes les dades de la base de dades i els documents associats."""

    def __init__(self, data_dao: DataManagementDAO, documents: DocumentDAO,
                 transaction_factory, storage_dir: str | Path):
        """Rep els DAOs de negoci i documents, i el directori de magatzem local."""
        self.data_dao = data_dao
        self.documents = documents
        self.transaction_factory = transaction_factory
        self.storage_dir = Path(storage_dir)

    def delete_all(self) -> ClearDataResult:
        """Esborra totes les dades de negoci i els documents del magatzem local.

        Només elimina del disc els fitxers que es trobin directament dins de
        `storage_dir`; els fitxers externs es descarten de la base de dades
        sense tocar-los.

        Returns:
            Nombre de fitxers eliminats i avisos dels que no s'han pogut
            eliminar.
        """
        paths = [Path(document.file_path) for document in self.documents.get_all()
                 if document.file_path]
        with self.transaction_factory():
            self.data_dao.delete_all()
        deleted = 0
        warnings = []
        storage = self.storage_dir.resolve()
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
        return ClearDataResult(deleted, tuple(warnings))
