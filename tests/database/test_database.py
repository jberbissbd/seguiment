from pathlib import Path

from tutopy.database.daos import academic_course_dao


class TestDatabase:

    def test_directori_correcte(self, db):
        assert Path(db.path).name == "database.db"
        assert Path(db.path).parent.exists()

    def test_creacio_taula_academic_courses(self, db):
        """Comprova que s'ha creat la taula academic_courses"""
        nom_taula = 'academic_courses'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_categories(self, db):
        """Comprova que s'ha creat la taula categories"""
        nom_taula = 'categories'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_students(self, db):
        """Comprova que s'ha creat la taula students"""
        nom_taula = 'students'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_notes(self, db):
        """Comprova que s'ha creat la taula notes"""
        nom_taula = 'notes'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_contacts(self, db):
        """Comprova que s'ha creat la taula contacts"""
        nom_taula = 'contacts'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_student_annotations(self, db):
        """Comprova que s'ha creat la taula student_annotations"""
        nom_taula = 'student_annotations'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_student_documents(self, db):
        """Comprova que s'ha creat la taula student_documents"""
        nom_taula = 'student_documents'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1