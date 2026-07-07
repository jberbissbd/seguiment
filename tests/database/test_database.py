from pathlib import Path
import uuid
from tutopy.models.messaging import CategoryNew, Category, AcademicCourse, AcademicCourseNew, Student, StudentNew, Note, NoteNew

class TestDatabasePaths:
    """
    Comprova que la base de dades es crea en el directori correcte
    """

    def test_directori_correcte(self, db):
        assert Path(db.path).name == "database.db"
        assert Path(db.path).parent.exists()

class TestCreationDatabaseTables:
    """
    Comprova que les taules es creen correctament
    """
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


class TestCreateRegisters:
    """Testeja la creació de registres a les taules"""

    def test_creacio_registre_categoria(self,db):
        """Verifica la creació d'un sol registre de la taula de categories"""
        categoria_test_individual = CategoryNew("Acadèmic")
        db.categories.create(categoria_test_individual)
        assert db.categories.get_all()[0] == Category(1,'Acadèmic')

    def test_creacio_registre_cursacademic(self,db):
        """Verifica la creació d'un sol registre de la taula de cursos acadèmics"""
        curs_test_individual = AcademicCourseNew("2025-2026")
        db.academic_courses.create(curs_test_individual)
        assert db.academic_courses.get_all()[0] == AcademicCourse(1,'2025-2026')

    def test_creacio_registre_alumne(self,db):
        """Verifica la creació d'un sol registre de la taula d'alumnes"""
        uuid_alumne_test = str(uuid.uuid4())
        alumne_test_individual = StudentNew(uuid_alumne_test, "Jordi", "Garcia", "4t A")
        alumne_creat = db.students.create(alumne_test_individual)
        assert db.students.get_all()[0] == Student(
            alumne_creat.id,
            alumne_creat.uuid,
            'Jordi',
            'Garcia',
            '4t A',
        )

    def test_creacio_anotacions(self,db):
        """Verifica la creació d'una anotacio"""
        anotacio_exemple = NoteNew(1,1,"2026-01-01",1,"Anotació exemple")
        db.notes.create(anotacio_exemple)
        registre = db.notes.get_all()[0]
        assert registre == Note(id=1,student_id=1,category_id=1,date='2026-01-01',course_id=1,content='Anotació exemple')

