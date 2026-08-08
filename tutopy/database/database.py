import os
import sqlite3
import sys
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
)


def _default_db_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "seguiment.db")
    return "seguiment.db"


class Database:
    """Gestor de la connexió SQLite.

    Proporciona accés a les DAOs (``.categories``, ``.students``,
    ``.notes``, ``.contacts``, ``.annotations``, ``.documents``).
    """

    def __init__(self, path: str = None):
        self.path = path or _default_db_path()
        self.conn: Optional[sqlite3.Connection] = None
        self.academic_courses: AcademicCourseDAO = None
        self.categories: CategoryDAO = None
        self.students: StudentDAO = None
        self.notes: NoteDAO = None
        self.contacts: ContactDAO = None
        self.annotations: AnnotationDAO = None
        self.documents: DocumentDAO = None
        self.student_group_history: StudentGroupHistoryDAO = None

    def connect(self):
        self.conn = sqlite3.connect(self.path)
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

    def _init_daos(self):
        self.academic_courses = AcademicCourseDAO(self.conn)
        self.categories = CategoryDAO(self.conn)
        self.students = StudentDAO(self.conn)
        self.notes = NoteDAO(self.conn, self.academic_courses)
        self.contacts = ContactDAO(self.conn)
        self.annotations = AnnotationDAO(self.conn)
        self.documents = DocumentDAO(self.conn)
        self.student_group_history = StudentGroupHistoryDAO(self.conn)

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
                uuid TEXT NOT NULL,
                name TEXT NOT NULL,
                surnames TEXT DEFAULT '',
                group_name TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                course_id INTEGER NOT NULL DEFAULT 0,
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
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS student_group_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                academic_course_id INTEGER,
                start_date TEXT NOT NULL,
                end_date TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (academic_course_id) REFERENCES academic_courses(id) ON DELETE SET NULL
            );
        """)
