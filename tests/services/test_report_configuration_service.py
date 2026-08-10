import pytest

from tutopy.application import create_services
from tutopy.models.messaging import CategoryNew
from tutopy.models.reporting import TermConfigurationNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def reporting(db):
    return create_services(db).report_configuration


def test_desa_i_actualitza_una_configuracio_per_curs_i_grup(db, reporting):
    course = db.academic_courses.get_or_create("2025-2026")
    created = reporting.save_term_configuration(TermConfigurationNew(
        course.id, "4t A", "2026-01-08", "2026-04-07"
    ))
    updated = reporting.save_term_configuration(TermConfigurationNew(
        course.id, " 4t A ", "2026-01-09", "2026-04-08"
    ))
    assert updated.id == created.id
    assert updated.group_name == "4t A"
    assert updated.second_term_start == "2026-01-09"
    assert len(reporting.get_term_configurations()) == 1


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        ("2026-01-07", "1r"),
        ("2026-01-08", "2n"),
        ("2026-04-06", "2n"),
        ("2026-04-07", "3r"),
    ],
)
def test_calcula_trimestre_amb_limits_inclusius(db, reporting, date, expected):
    course = db.academic_courses.get_or_create("2025-2026")
    reporting.save_term_configuration(TermConfigurationNew(
        course.id, "4t A", "2026-01-08", "2026-04-07"
    ))
    assert reporting.term_for_date(course.id, "4t A", date) == expected


def test_sense_configuracio_no_assigna_trimestre(db, reporting):
    course = db.academic_courses.get_or_create("2025-2026")
    assert reporting.term_for_date(course.id, "4t A", "2026-02-01") is None


def test_rebutja_dates_invertides_o_fora_del_curs(db, reporting):
    course = db.academic_courses.get_or_create("2025-2026")
    with pytest.raises(ValidationError, match="tercer trimestre"):
        reporting.save_term_configuration(TermConfigurationNew(
            course.id, "4t A", "2026-04-07", "2026-01-08"
        ))
    with pytest.raises(ValidationError, match="pertànyer al curs"):
        reporting.save_term_configuration(TermConfigurationNew(
            course.id, "4t A", "2026-01-08", "2026-09-01"
        ))


def test_rebutja_curs_inexistent(db, reporting):
    with pytest.raises(EntityNotFoundError):
        reporting.save_term_configuration(TermConfigurationNew(
            999, "4t A", "2026-01-08", "2026-04-07"
        ))


def test_elimina_configuracio(db, reporting):
    course = db.academic_courses.get_or_create("2025-2026")
    configuration = reporting.save_term_configuration(TermConfigurationNew(
        course.id, "4t A", "2026-01-08", "2026-04-07"
    ))
    reporting.delete_term_configuration(configuration.id)
    assert reporting.get_term_configurations() == []
    with pytest.raises(EntityNotFoundError):
        reporting.delete_term_configuration(configuration.id)


def test_desa_i_recupera_ordre_de_categories(db, reporting):
    academic = db.categories.create(CategoryNew("Acadèmic"))
    family = db.categories.create(CategoryNew("Família"))
    conduct = db.categories.create(CategoryNew("Conducta"))
    ordered = reporting.set_category_order([family.id, conduct.id, academic.id])
    assert [category.id for category in ordered] == [family.id, conduct.id, academic.id]
    assert [category.id for category in reporting.get_ordered_categories()] == [
        family.id, conduct.id, academic.id
    ]


def test_categories_noves_apareixen_al_final(db, reporting):
    academic = db.categories.create(CategoryNew("Acadèmic"))
    family = db.categories.create(CategoryNew("Família"))
    reporting.set_category_order([family.id, academic.id])
    conduct = db.categories.create(CategoryNew("Conducta"))
    assert [category.id for category in reporting.get_ordered_categories()] == [
        family.id, academic.id, conduct.id
    ]


@pytest.mark.parametrize("order", [[1, 1], [1], [1, "2"]])
def test_rebutja_ordres_incomplets_duplicats_o_invalids(db, reporting, order):
    db.categories.create(CategoryNew("A"))
    db.categories.create(CategoryNew("B"))
    with pytest.raises(ValidationError):
        reporting.set_category_order(order)
