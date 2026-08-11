from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew


def test_exporta_informe_i_documents_en_carpetes_per_curs(db, tmp_path):
    services = create_services(db)
    services.documents.storage_dir = tmp_path / "managed"
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Bona evolució"
    ))
    first = tmp_path / "primer.pdf"
    second = tmp_path / "segon.txt"
    first.write_bytes(b"PDF")
    second.write_text("Text", encoding="utf-8")
    services.documents.import_file(
        student.id, "Informe", "Valoració", str(first), "2026-02-03"
    )
    services.documents.import_file(
        student.id, "Acta", "Valoració", str(second), "2024-10-10"
    )

    root = services.student_exports.export_student(
        student.id, tmp_path / "exportacio", "xlsx"
    )

    assert root == tmp_path / "exportacio" / "Martí, Laia"
    assert (root / "informe.xlsx").is_file()
    assert (root / "2025-2026" / "Valoració.pdf").read_bytes() == b"PDF"
    assert (root / "2024-2025" / "Valoració.txt").read_text(encoding="utf-8") == "Text"
