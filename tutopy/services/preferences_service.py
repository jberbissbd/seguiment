"""Preferències generals de l'aplicació, no vinculades a cap domini concret."""

UPDATE_CHECK_ENABLED_KEY = "update_check_enabled"


class PreferencesService:
    """Embolcall tipat sobre `SettingsDAO` per a les preferències generals."""

    def __init__(self, settings_dao):
        """Rep el DAO de preferències clau-valor."""
        self.settings_dao = settings_dao

    def is_update_check_enabled(self) -> bool:
        """Indica si cal comprovar si hi ha versions noves en iniciar.

        Activat per defecte si encara no s'ha desat cap preferència.
        """
        return self.settings_dao.get(UPDATE_CHECK_ENABLED_KEY) != "0"

    def set_update_check_enabled(self, enabled: bool) -> None:
        """Desa si cal comprovar si hi ha versions noves en iniciar."""
        self.settings_dao.set(UPDATE_CHECK_ENABLED_KEY, "1" if enabled else "0")
