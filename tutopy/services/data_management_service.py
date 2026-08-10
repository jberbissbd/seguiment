from pathlib import Path

from tutopy.database.daos.data_management_dao import DataManagementDAO
from tutopy.database.daos.document_dao import DocumentDAO
from tutopy.models.bulk_import import ClearDataResult


class DataManagementService:
    def __init__(self, data_dao: DataManagementDAO, documents: DocumentDAO,
                 transaction_factory, storage_dir: str | Path):
        self.data_dao = data_dao
        self.documents = documents
        self.transaction_factory = transaction_factory
        self.storage_dir = Path(storage_dir)

    def delete_all(self) -> ClearDataResult:
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
