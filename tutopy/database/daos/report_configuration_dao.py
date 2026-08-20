import sqlite3

from tutopy.models.reporting import TermConfiguration, TermConfigurationNew


class ReportConfigurationPersistenceError(RuntimeError):
    """La configuració d'informes no s'ha pogut persistir."""


class ReportConfigurationDAO:
    """Persistència de les preferències utilitzades pels informes XLSX."""

    def __init__(self, conn):
        self.conn = conn

    def get_term_configurations(self) -> list[TermConfiguration]:
        rows = self.conn.execute(
            "SELECT id, academic_course_id, group_name, second_term_start, "
            "third_term_start FROM term_configurations "
            "ORDER BY academic_course_id DESC, group_name"
        ).fetchall()
        return [TermConfiguration(**row) for row in rows]

    def get_term_configuration(
        self, academic_course_id: int, group_name: str
    ) -> TermConfiguration | None:
        row = self.conn.execute(
            "SELECT id, academic_course_id, group_name, second_term_start, "
            "third_term_start FROM term_configurations "
            "WHERE academic_course_id = ? AND group_name = ?",
            (academic_course_id, group_name),
        ).fetchone()
        return TermConfiguration(**row) if row else None

    def save_term_configuration(self, data: TermConfigurationNew) -> TermConfiguration:
        self.conn.execute(
            "INSERT INTO term_configurations "
            "(academic_course_id, group_name, second_term_start, third_term_start) "
            "VALUES (?, ?, ?, ?) ON CONFLICT(academic_course_id, group_name) "
            "DO UPDATE SET second_term_start=excluded.second_term_start, "
            "third_term_start=excluded.third_term_start",
            (data.academic_course_id, data.group_name,
             data.second_term_start, data.third_term_start),
        )
        self.conn.commit()
        return self.get_term_configuration(data.academic_course_id, data.group_name)

    def delete_term_configuration(self, configuration_id: int) -> None:
        self.conn.execute("DELETE FROM term_configurations WHERE id = ?", (configuration_id,))
        self.conn.commit()

    def get_category_order(self) -> list[int]:
        rows = self.conn.execute(
            "SELECT category_id FROM category_export_order ORDER BY position"
        ).fetchall()
        return [row[0] for row in rows]

    def set_category_order(self, category_ids: list[int]) -> None:
        self.conn.execute("DELETE FROM category_export_order")
        self.conn.executemany(
            "INSERT INTO category_export_order (category_id, position) VALUES (?, ?)",
            [(category_id, position) for position, category_id in enumerate(category_ids)],
        )
        self.conn.commit()

    def get_setting(self, key: str) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM report_settings WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def set_setting(self, key: str, value: str) -> None:
        try:
            self.conn.execute(
                "INSERT INTO report_settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            self.conn.commit()
        except sqlite3.Error as error:
            raise ReportConfigurationPersistenceError from error

    def delete_setting(self, key: str) -> None:
        try:
            self.conn.execute("DELETE FROM report_settings WHERE key = ?", (key,))
            self.conn.commit()
        except sqlite3.Error as error:
            raise ReportConfigurationPersistenceError from error
