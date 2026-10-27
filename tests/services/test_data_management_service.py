from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, StudentDocumentNew, StudentNew, StudentPhoto
from tutopy.services.data_management_service import DataManagementService
from tutopy.models.reporting import TermConfigurationNew


def test_delete_all_buida_entitats_i_nomes_fitxers_gestionats(db, tmp_path):
    services = create_services(db)
    student = services.students.create(StudentNew("Ada", "Lovelace", "4t A"))
    services.categories.create(CategoryNew("Acadèmic"))
    course = services.academic_courses.get_or_create("2025-2026")
    services.report_configuration.save_term_configuration(TermConfigurationNew(
        course.id, "4t A", "2026-01-08", "2026-04-07"
    ))
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
    photos_storage = tmp_path / "photos"
    photos_storage.mkdir()
    managed_photo = photos_storage / "managed.png"
    managed_photo.write_text("managed photo")
    other_student = services.students.create(StudentNew("Bet", "Puig", "4t A"))
    external_photo = tmp_path / "external.png"
    external_photo.write_text("external photo")
    db.photos.set(StudentPhoto(student.id, "managed.png", "a.png", str(managed_photo)))
    db.photos.set(StudentPhoto(other_student.id, "external.png", "b.png", str(external_photo)))
    service = DataManagementService(db.data_management, db.documents,
                                    db.transaction, storage,
                                    photo_dao=db.photos, photos_storage_dir=photos_storage)
    result = service.delete_all()
    assert db.students.get_all() == []
    assert db.categories.get_all() == []
    assert db.documents.get_all() == []
    assert db.photos.get_all() == []
    assert db.report_configuration.get_term_configurations() == []
    assert not managed.exists()
    assert external.exists()
    assert not managed_photo.exists()
    assert external_photo.exists()
    assert result.deleted_files == 2
