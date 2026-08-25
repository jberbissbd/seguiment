"""DAO per a operacions globals de manteniment de la base de dades."""


class DataManagementDAO:
    """Operacions globals de persistència, sense lògica de presentació."""

    TABLES = (
        "notes", "contacts", "student_annotations", "student_documents",
        "student_group_history", "term_configurations", "category_export_order",
        "students", "categories", "academic_courses",
    )

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def delete_all(self) -> None:
        """Buida totes les taules de dades i reinicia els comptadors ``AUTOINCREMENT``."""
        for table in self.TABLES:
            self.conn.execute(f"DELETE FROM {table}")
        placeholders = ", ".join("?" for _ in self.TABLES)
        self.conn.execute(
            f"DELETE FROM sqlite_sequence WHERE name IN ({placeholders})",
            self.TABLES,
        )
        self.conn.commit()
