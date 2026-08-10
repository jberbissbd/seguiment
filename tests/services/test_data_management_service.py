from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, StudentDocumentNew, StudentNew
from tutopy.services.data_management_service import DataManagementService


def test_delete_all_buida_entitats_i_nomes_fitxers_gestionats(db, tmp_path):
    services = create_services(db)
    student = services.students.create(StudentNew("Ada", "Lovelace", "4t A"))
    services.categories.create(CategoryNew("Acadèmic"))
    storage = tmp_path / "documents"
    storage.mkdir()
    managed = storage / "managed.pdf"
    managed.write_text("managed")
    external = tmp_path / "external.pdf"
    external.write_text("external")
    db.documents.create(StudentDocumentNew(student.id, "Gestionat", "",
                                             "managed.pdf", "a.pdf", str(managed)))
    db.documents.create(StudentDocumentNew(student.id, "Extern", "",
                                             "external.pdf", "b.pdf", str(external)))
    service = DataManagementService(db.data_management, db.documents,
                                    db.transaction, storage)
    result = service.delete_all()
    assert db.students.get_all() == []
    assert db.categories.get_all() == []
    assert db.documents.get_all() == []
    assert not managed.exists()
    assert external.exists()
    assert result.deleted_files == 1
