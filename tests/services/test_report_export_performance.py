import pytest

from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew


@pytest.mark.parametrize("report_format", ["xlsx", "docx", "odt", "pdf"])
@pytest.mark.parametrize("student_count", [1, 5])
def test_exportacio_massiva_d_informes_te_lectures_constants(
    db, tmp_path, report_format, student_count
):
    services = create_services(db)
    category = services.categories.create(CategoryNew("Seguiment"))
    student_ids = []
    for index in range(student_count):
        student = services.students.create(
            StudentNew(f"Nom {index}", "Cognom", "1A")
        )
        services.notes.create(
            NoteNew(
                student.id, category.id, "2026-02-01", 0, "Evolució positiva"
            )
        )
        student_ids.append(student.id)

    statements = []
    db.conn._connection.set_trace_callback(statements.append)
    try:
        result = services.student_exports.export_students(
            student_ids, tmp_path / report_format, report_format
        )
    finally:
        db.conn._connection.set_trace_callback(None)

    reads = [item for item in statements if item.lstrip().upper().startswith("SELECT")]
    assert result.exported == student_count
    assert len(reads) == 6


@pytest.mark.parametrize("student_count", [1, 5])
def test_exportacio_amb_documents_te_lectures_constants(
    db, tmp_path, student_count
):
    services = create_services(db)
    services.documents.storage_dir = tmp_path / "managed"
    category = services.categories.create(CategoryNew("Seguiment"))
    student_ids = []
    for index in range(student_count):
        student = services.students.create(
            StudentNew(f"Nom {index}", "Cognom", "1A")
        )
        services.notes.create(
            NoteNew(student.id, category.id, "2026-02-01", 0, "Seguiment")
        )
        for document_index in range(2):
            source = tmp_path / f"document-{index}-{document_index}.txt"
            source.write_text("contingut", encoding="utf-8")
            services.documents.import_file(
                student.id, "Document", f"Annex {document_index}",
                str(source), "2026-02-01",
            )
        student_ids.append(student.id)

    statements = []
    db.conn._connection.set_trace_callback(statements.append)
    try:
        result = services.student_exports.export_students(
            student_ids, tmp_path / "informes", "xlsx", include_documents=True
        )
    finally:
        db.conn._connection.set_trace_callback(None)

    reads = [item for item in statements if item.lstrip().upper().startswith("SELECT")]
    assert result.exported == student_count
    assert len(reads) == 9
