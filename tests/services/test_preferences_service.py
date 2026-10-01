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
