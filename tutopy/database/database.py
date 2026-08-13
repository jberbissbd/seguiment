import os
import sqlite3
import sys
from contextlib import contextmanager
from typing import Optional
from .daos import (
    AcademicCourseDAO,
    CategoryDAO,
    StudentDAO,
    NoteDAO,
    ContactDAO,
    AnnotationDAO,
    DocumentDAO,
    StudentGroupHistoryDAO,
    DataManagementDAO,
    ReportConfigurationDAO,
    StatisticsDAO,
)


def _default_db_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "seguiment.db")
    return "seguiment.db"


class ManagedConnection:
    """Fa que els ``commit`` dels DAOs respectin una transacció exterior."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._transaction_depth = 0

    @property
    def row_factory(self):
        return self._connection.row_factory

    @row_factory.setter
    def row_factory(self, value):
        self._connection.row_factory = value

    def execute(self, *args, **kwargs):
        return self._connection.execute(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._connection.executescript(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._connection.executemany(*args, **kwargs)

    def commit(self):
        if self._transaction_depth == 0:
            self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    @contextmanager
    def transaction(self):
        outermost = self._transaction_depth == 0
        if outermost:
            self._connection.execute("BEGIN")
        self._transaction_depth += 1
        try:
            yield
        except Exception:
            self._transaction_depth -= 1
            if outermost:
                self._connection.rollback()
            raise
        else:
            self._transaction_depth -= 1
            if outermost:
                self._connection.commit()


class Database:
    """Gestor de la connexió SQLite.

    Proporciona accés a les DAOs (``.categories``, ``.students``,
    ``.notes``, ``.contacts``, ``.annotations``, ``.documents``).
    """

    def __init__(self, path: str = None):
        self.path = path or _default_db_path()
        self.conn: Optional[ManagedConnection] = None
        self.academic_courses: AcademicCourseDAO = None
        self.categories: CategoryDAO = None
        self.students: StudentDAO = None
        self.notes: NoteDAO = None
        self.contacts: ContactDAO = None
        self.annotations: AnnotationDAO = None
        self.documents: DocumentDAO = None
        self.student_group_history: StudentGroupHistoryDAO = None
        self.data_management: DataManagementDAO = None
        self.report_configuration: ReportConfigurationDAO = None
        self.statistics: StatisticsDAO = None

    def connect(self):
        self.conn = ManagedConnection(sqlite3.connect(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._init_daos()
        return self

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def commit(self):
        if self.conn:
            self.conn.commit()

    def transaction(self):
        """Context transaccional compartit pels serveis coordinadors."""
        if self.conn is None:
            raise RuntimeError("La base de dades no està connectada.")
        return self.conn.transaction()

    def _init_daos(self):
        self.academic_courses = AcademicCourseDAO(self.conn)
        self.categories = CategoryDAO(self.conn)
        self.students = StudentDAO(self.conn)
        self.notes = NoteDAO(self.conn)
        self.contacts = ContactDAO(self.conn)
        self.annotations = AnnotationDAO(self.conn)
        self.documents = DocumentDAO(self.conn)
        self.student_group_history = StudentGroupHistoryDAO(self.conn)
        self.data_management = DataManagementDAO(self.conn)
        self.report_configuration = ReportConfigurationDAO(self.conn)
        self.statistics = StatisticsDAO(self.conn)

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS academic_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                surnames TEXT DEFAULT '',
                group_name TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                course_id INTEGER NOT NULL,
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
                file_path TEXT NOT NULL DEFAULT '',
                date TEXT NOT NULL DEFAULT '',
                course_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES academic_courses(id) ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS student_group_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                academic_course_id INTEGER,
                start_date TEXT NOT NULL,
                end_date TEXT,
                CHECK (end_date IS NULL OR end_date >= start_date),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (academic_course_id) REFERENCES academic_courses(id) ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS term_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_course_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                second_term_start TEXT NOT NULL,
                third_term_start TEXT NOT NULL,
                UNIQUE (academic_course_id, group_name),
                CHECK (third_term_start > second_term_start),
                FOREIGN KEY (academic_course_id)
                    REFERENCES academic_courses(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS category_export_order (
                category_id INTEGER PRIMARY KEY,
                position INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS report_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_uuid
                ON students(uuid);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_current_group_per_student
                ON student_group_history(student_id) WHERE end_date IS NULL;
            CREATE INDEX IF NOT EXISTS idx_notes_student ON notes(student_id);
            CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category_id);
            CREATE INDEX IF NOT EXISTS idx_notes_course ON notes(course_id);
            CREATE INDEX IF NOT EXISTS idx_notes_date ON notes(date);
            CREATE INDEX IF NOT EXISTS idx_notes_course_date ON notes(course_id, date);
            CREATE INDEX IF NOT EXISTS idx_notes_category_date ON notes(category_id, date);
            CREATE INDEX IF NOT EXISTS idx_contacts_student ON contacts(student_id);
            CREATE INDEX IF NOT EXISTS idx_annotations_student
                ON student_annotations(student_id);
            CREATE INDEX IF NOT EXISTS idx_documents_student
                ON student_documents(student_id);
            CREATE INDEX IF NOT EXISTS idx_group_history_student
                ON student_group_history(student_id);
            CREATE INDEX IF NOT EXISTS idx_term_config_course_group
                ON term_configurations(academic_course_id, group_name);
            CREATE INDEX IF NOT EXISTS idx_students_group ON students(group_name);
        """)
