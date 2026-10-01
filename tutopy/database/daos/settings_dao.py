"""DAO per a les preferències generals de l'aplicació."""

import sqlite3


class SettingsPersistenceError(RuntimeError):
    """La preferència no s'ha pogut persistir."""


class SettingsDAO:
    """Persistència clau-valor de les preferències generals de l'aplicació."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get(self, key: str) -> str | None:
        """Retorna el valor d'una preferència, o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        """Crea o actualitza una preferència.

        Raises:
            SettingsPersistenceError: Si SQLite rebutja l'escriptura.
        """
        try:
            self.conn.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            self.conn.commit()
        except sqlite3.Error as error:
            raise SettingsPersistenceError from error

    def delete(self, key: str) -> None:
        """Elimina una preferència.

        Raises:
            SettingsPersistenceError: Si SQLite rebutja l'eliminació.
        """
        try:
            self.conn.execute("DELETE FROM app_settings WHERE key = ?", (key,))
            self.conn.commit()
        except sqlite3.Error as error:
            raise SettingsPersistenceError from error
