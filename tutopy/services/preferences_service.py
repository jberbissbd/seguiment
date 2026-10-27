"""Preferències generals de l'aplicació, no vinculades a cap domini concret."""

UPDATE_CHECK_ENABLED_KEY = "update_check_enabled"

CLASSROOM_COLUMN_PATTERN_KEY = "classroom_default_column_pattern"
CLASSROOM_TEACHER_MODE_KEY = "classroom_default_teacher_mode"
CLASSROOM_TEACHER_POSITION_KEY = "classroom_default_teacher_position"
CLASSROOM_LEFTOVER_CRITERION_KEY = "classroom_default_leftover_criterion"
CLASSROOM_FILL_ORDER_KEY = "classroom_default_fill_order"
CLASSROOM_FILL_RANDOM_KEY = "classroom_default_fill_random"

CLASSROOM_COLUMN_PATTERN_DEFAULT = "2-2-2"
CLASSROOM_TEACHER_MODE_DEFAULT = "strip"
CLASSROOM_TEACHER_POSITION_DEFAULT = "center"
CLASSROOM_LEFTOVER_CRITERION_DEFAULT = "back"
CLASSROOM_FILL_ORDER_DEFAULT = "rows"


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

    def default_column_pattern(self) -> str:
        """Retorna el patró de columnes amb què comença una plantilla nova."""
        return self._get(CLASSROOM_COLUMN_PATTERN_KEY, CLASSROOM_COLUMN_PATTERN_DEFAULT)

    def set_default_column_pattern(self, pattern: str) -> None:
        """Desa el patró de columnes per defecte de les plantilles noves."""
        self.settings_dao.set(CLASSROOM_COLUMN_PATTERN_KEY, pattern)

    def default_teacher_mode(self) -> str:
        """Retorna el mode de taula del professor per defecte (`"strip"` o `"grid"`)."""
        return self._get(CLASSROOM_TEACHER_MODE_KEY, CLASSROOM_TEACHER_MODE_DEFAULT)

    def set_default_teacher_mode(self, mode: str) -> None:
        """Desa el mode de taula del professor per defecte."""
        self.settings_dao.set(CLASSROOM_TEACHER_MODE_KEY, mode)

    def default_teacher_position(self) -> str:
        """Retorna la posició de la franja del professor per defecte."""
        return self._get(CLASSROOM_TEACHER_POSITION_KEY, CLASSROOM_TEACHER_POSITION_DEFAULT)

    def set_default_teacher_position(self, position: str) -> None:
        """Desa la posició de la franja del professor per defecte."""
        self.settings_dao.set(CLASSROOM_TEACHER_POSITION_KEY, position)

    def default_leftover_criterion(self) -> str:
        """Retorna el criteri de seients sobrants per defecte."""
        return self._get(CLASSROOM_LEFTOVER_CRITERION_KEY, CLASSROOM_LEFTOVER_CRITERION_DEFAULT)

    def set_default_leftover_criterion(self, criterion: str) -> None:
        """Desa el criteri de seients sobrants per defecte."""
        self.settings_dao.set(CLASSROOM_LEFTOVER_CRITERION_KEY, criterion)

    def default_fill_order(self) -> str:
        """Retorna el criteri d'ordenació de l'ompliment per defecte (`"rows"`/`"blocks"`)."""
        return self._get(CLASSROOM_FILL_ORDER_KEY, CLASSROOM_FILL_ORDER_DEFAULT)

    def set_default_fill_order(self, order: str) -> None:
        """Desa el criteri d'ordenació de l'ompliment per defecte."""
        self.settings_dao.set(CLASSROOM_FILL_ORDER_KEY, order)

    def default_fill_random(self) -> bool:
        """Indica si l'ompliment per defecte és aleatori (alfabètic si `False`)."""
        return self.settings_dao.get(CLASSROOM_FILL_RANDOM_KEY) == "1"

    def set_default_fill_random(self, random: bool) -> None:
        """Desa si l'ompliment per defecte ha de ser aleatori."""
        self.settings_dao.set(CLASSROOM_FILL_RANDOM_KEY, "1" if random else "0")

    def _get(self, key: str, default: str) -> str:
        value = self.settings_dao.get(key)
        return value if value is not None else default
