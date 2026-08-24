import pytest

from tutopy.application import create_services
from tutopy.models.messaging import StudentNew
from tutopy.models.student_bulk import StudentBulkUpdate
from tutopy.services.exceptions import ValidationError


def test_edicio_massiva_actualitza_noms_i_historials(db):
    services = create_services(db)
    first = services.students.create(StudentNew("Anna", "Serra", "1A"))
    second = services.students.create(StudentNew("Biel", "Puig", "1A"))

    result = services.students.bulk_update([
        StudentBulkUpdate(first.id, "Anna Maria", "Serra", "2B"),
        StudentBulkUpdate(second.id, "Biel", "Puig-Soler", "1A"),
    ], "2026-09-01")

    assert result.updated == 2
    assert result.group_changes == 1
    assert services.students.get_by_id(first.id).group_name == "2B"
    assert services.students.get_by_id(second.id).surnames == "Puig-Soler"
    history = services.students.get_group_history(first.id)
    assert history[-1].group_name == "2B"
    assert history[-1].start_date == "2026-09-01"


def test_edicio_massiva_valida_tot_el_lot_abans_d_escriure(db):
    services = create_services(db)
    first = services.students.create(StudentNew("Anna", "Serra", "1A"))
    second = services.students.create(StudentNew("Biel", "Puig", "1A"))

    changes = [
        StudentBulkUpdate(first.id, "Anna modificada", "Serra", "2B"),
        StudentBulkUpdate(second.id, "", "Puig", "1A"),
    ]
    with pytest.raises(ValidationError):
        services.students.bulk_update(changes, "2026-09-01")

    assert services.students.get_by_id(first.id) == first
    assert services.students.get_by_id(second.id) == second


def test_edicio_massiva_resol_el_curs_academic_una_sola_vegada(db):
    services = create_services(db)
    students = [
        services.students.create(StudentNew(f"Nom {index}", "Cognom", "1A"))
        for index in range(5)
    ]

    statements = []
    db.conn._connection.set_trace_callback(statements.append)
    try:
        result = services.students.bulk_update(
            [StudentBulkUpdate(item.id, item.name, item.surnames, "2B")
             for item in students],
            "2026-09-01",
        )
    finally:
        db.conn._connection.set_trace_callback(None)

    assert result.group_changes == 5
    resolution_statements = [
        item for item in statements
        if "academic_courses" in item and "WHERE course" in item
    ]
    assert len(resolution_statements) == 1


def test_cancel_lacio_de_l_edicio_massiva_fa_rollback(db):
    services = create_services(db)
    students = [
        services.students.create(StudentNew(f"Nom {index}", "Cognom", "1A"))
        for index in range(3)
    ]
    progress = []

    result = services.students.bulk_update(
        [StudentBulkUpdate(item.id, item.name, item.surnames, "2B")
         for item in students],
        "2026-09-01",
        progress_callback=lambda completed, total: progress.append((completed, total)),
        cancel_requested=lambda: bool(progress),
    )

    assert result.cancelled is True
    assert progress == [(1, 3)]
    assert {item.group_name for item in services.students.get_all()} == {"1A"}
