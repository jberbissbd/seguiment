import os
import sqlite3
import sys
from typing import Optional

def _default_db_path() -> str:
    """Retorna la ruta per defecte de la base de dades.

    En mode desenvolupament: directori actual (cwd).
    En PyInstaller (--onefile): directori de l'executable.
    """
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "seguiment.db")
    return "seguiment.db"


class Database:
    """Gestor de la base de dades SQLite.

    Manté la connexió, crea les taules i proporciona mètodes CRUD
    per a cada entitat del model.
    """

    def __init__(self, path: str = None):
        """Obre (o crea) la base de dades al fitxer indicat.

        Args:
            path: Ruta al fitxer SQLite. Si és ``None``, usa la ruta
                  per defecte (directori de l'executable o cwd).
        """
        self.path = path or _default_db_path()
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Estableix la connexió i crea les taules si no existeixen."""
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        return self

    def close(self):
        """Confirma els canvis pendents i tanca la connexió."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def commit(self):
        """Força un commit de la transacció actual."""
        if self.conn:
            self.conn.commit()

    def _create_tables(self):
        """Crea les taules del model si no existeixen al disc."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS academic_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT DEFAULT '',
                group_name TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                course INTEGER NOT NULL DEFAULT 0,
                content TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
                FOREIGN KEY (course_id) REFERENCES academic_courses(id) ON DELETE RESTRICT
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                phone TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS student_annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS student_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                uuid_filename TEXT NOT NULL,
                original_filename TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
        """)
