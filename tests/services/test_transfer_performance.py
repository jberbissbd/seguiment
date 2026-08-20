import pytest

from tutopy.application import create_services
from tutopy.models.messaging import StudentNew


@pytest.mark.parametrize("student_count", [1, 10])
def test_exportacio_transferencia_te_un_nombre_constant_de_lectures(
    db, tmp_path, monkeypatch, student_count
):
    services = create_services(db)
    student_ids = [
        services.students.create(StudentNew(f"Nom {index}", "Cognom", "1A")).id
        for index in range(student_count)
    ]
    monkeypatch.setattr(
        services.transfers,
        "_encrypt_file",
        lambda _source, destination, _password: destination.write_bytes(b"xifrat"),
    )
    statements = []
    db.conn._connection.set_trace_callback(statements.append)
    try:
        services.transfers.export_students(
            student_ids, tmp_path / "alumnes.tpy", "contrasenya-segura"
        )
    finally:
        db.conn._connection.set_trace_callback(None)

    reads = [item for item in statements if item.lstrip().upper().startswith("SELECT")]
    assert len(reads) == 8
