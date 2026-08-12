from datetime import date

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


def test_exporta_diversos_alumnes_i_separa_homonims(db, tmp_path):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Acadèmic"))
    first = services.students.create(StudentNew("Alex", "Garcia", "2n A"))
    second = services.students.create(StudentNew("Alex", "Garcia", "2n B"))
    for student in (first, second):
        services.notes.create(NoteNew(
            student.id, category.id, "2026-02-01", 0, "Seguiment"
        ))

    result = services.student_exports.export_students(
        [first.id, second.id], tmp_path / "lots", "docx"
    )
    root = tmp_path / "lots" / f"Informes {date.today().isoformat()}"
    assert result.destination == str(root)
    assert result.exported == 2
    assert result.failures == ()
    assert (root / "Garcia, Alex" / "informe.docx").is_file()
    assert (root / "Garcia, Alex (2)" / "informe.docx").is_file()


def test_exportacio_multiple_continua_si_un_alumne_no_te_notes(db, tmp_path):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Acadèmic"))
    valid = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    empty = services.students.create(StudentNew("Pau", "Puig", "3r A"))
    services.notes.create(NoteNew(
        valid.id, category.id, "2026-02-01", 0, "Seguiment"
    ))

    result = services.student_exports.export_students(
        [empty.id, valid.id], tmp_path / "lots", "xlsx"
    )
    assert result.exported == 1
    assert len(result.failures) == 1
    assert result.failures[0].student_name == "Puig, Pau"
