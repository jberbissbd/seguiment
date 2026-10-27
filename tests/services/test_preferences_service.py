from tutopy.services.preferences_service import PreferencesService


def test_comprovacio_de_versio_activada_per_defecte(db):
    preferences = PreferencesService(db.settings)

    assert preferences.is_update_check_enabled() is True


def test_desactivar_i_reactivar_la_comprovacio_de_versio(db):
    preferences = PreferencesService(db.settings)

    preferences.set_update_check_enabled(False)
    assert preferences.is_update_check_enabled() is False

    preferences.set_update_check_enabled(True)
    assert preferences.is_update_check_enabled() is True


def test_preferencies_de_distribucio_tenen_valors_per_defecte(db):
    preferences = PreferencesService(db.settings)

    assert preferences.default_column_pattern() == "2-2-2"
    assert preferences.default_teacher_mode() == "strip"
    assert preferences.default_teacher_position() == "center"
    assert preferences.default_leftover_criterion() == "back"
    assert preferences.default_fill_order() == "rows"
    assert preferences.default_fill_random() is False


def test_preferencies_de_distribucio_es_poden_desar(db):
    preferences = PreferencesService(db.settings)

    preferences.set_default_column_pattern("3-3")
    preferences.set_default_teacher_mode("grid")
    preferences.set_default_teacher_position("left")
    preferences.set_default_leftover_criterion("front")
    preferences.set_default_fill_order("blocks")
    preferences.set_default_fill_random(True)

    assert preferences.default_column_pattern() == "3-3"
    assert preferences.default_teacher_mode() == "grid"
    assert preferences.default_teacher_position() == "left"
    assert preferences.default_leftover_criterion() == "front"
    assert preferences.default_fill_order() == "blocks"
    assert preferences.default_fill_random() is True
