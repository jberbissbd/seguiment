import pytest

from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.models.statistics import StatisticsFilters
from tutopy.services.exceptions import ValidationError


def test_resume_agrega_notes_i_conserva_alumnes_sense_notes(db):
    services = create_services(db)
    laia = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    services.students.create(StudentNew("Pau", "Puig", "4t A"))
    services.students.create(StudentNew("Joana", "Serra", "3r B"))
    academic = services.categories.create(CategoryNew("Acadèmic"))
    family = services.categories.create(CategoryNew("Família"))
    services.notes.create(NoteNew(
        laia.id, academic.id, "2026-01-10", 0, "Primera"
    ))
    services.notes.create(NoteNew(
        laia.id, family.id, "2026-02-10", 0, "Segona"
    ))

    snapshot = services.statistics.get_snapshot(
        StatisticsFilters(group_name="4t A")
    )

    assert snapshot.note_count == 2
    assert snapshot.student_count == 2
    assert snapshot.students_with_notes == 1
    assert snapshot.students_without_notes == 1
    assert snapshot.average_per_student == 1.0
    assert [(item.label, item.value) for item in snapshot.by_month] == [
        ("Gener 2026", 1), ("Febrer 2026", 1)
    ]
    assert {item.label: item.value for item in snapshot.by_category} == {
        "Acadèmic": 1, "Família": 1,
    }
    assert [(item.student_name, item.note_count) for item in snapshot.by_student] == [
        ("Martí, Laia", 2), ("Puig, Pau", 0),
    ]


def test_filtres_de_categoria_i_dates_sapliquen_a_tots_els_resultats(db):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    academic = services.categories.create(CategoryNew("Acadèmic"))
    family = services.categories.create(CategoryNew("Família"))
    services.notes.create(NoteNew(student.id, academic.id, "2025-10-01", 0, "A"))
    services.notes.create(NoteNew(student.id, academic.id, "2026-02-01", 0, "B"))
    services.notes.create(NoteNew(student.id, family.id, "2026-02-02", 0, "C"))

    snapshot = services.statistics.get_snapshot(StatisticsFilters(
        category_id=academic.id, date_from="2026-01-01", date_to="2026-12-31"
    ))

    assert snapshot.note_count == 1
    assert snapshot.by_category[0].label == "Acadèmic"
    assert snapshot.by_student[0].note_count == 1


def test_rebutja_interval_invertit_i_entitats_inexistents(db):
    services = create_services(db)
    with pytest.raises(ValidationError, match="data inicial"):
        services.statistics.get_snapshot(StatisticsFilters(
            date_from="2026-05-01", date_to="2026-01-01"
        ))
    with pytest.raises(ValidationError, match="categoria.*no existeix"):
        services.statistics.get_snapshot(StatisticsFilters(category_id=999))


def test_selector_de_cursos_omet_cursos_sense_notes_despres_deditar(db):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    note = services.notes.create(NoteNew(
        student.id, category.id, "2026-05-10", 0, "Nota inicial"
    ))
    old_course = services.academic_courses.get_by_course("2025-2026")

    note.date = "2026-09-10"
    services.notes.update(note)

    assert services.academic_courses.get_by_course("2025-2026") == old_course
    assert [course.course for course in services.statistics.get_available_courses()] == [
        "2026-2027"
    ]


def test_nom_del_mes_es_localitzat_en_catala():
    from tutopy.services.statistics_service import StatisticsService

    assert StatisticsService._month_label("2026-09") == "Setembre 2026"
