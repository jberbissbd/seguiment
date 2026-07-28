from pathlib import Path
import uuid, pytest
from tutopy.models.messaging import CategoryNew, Category, AcademicCourse, AcademicCourseNew, Student, StudentNew, Note, NoteNew,NoteRecord, ContactNew, Contact, StudentAnnotation, StudentAnnotationNew

class TestDatabasePaths:
    """
    Comprova que la base de dades es crea en el directori correcte
    """

    def test_directori_correcte(self, db):
        """
        Comprova els directoris per a la base de dades.
        """
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

    def test_creacio_registre(self,db):
        """Verifica la creació d'una anotacio"""
        anotacio_exemple = NoteNew(1,1,"2026-01-01",1,"Anotació exemple")
        db.notes.create(anotacio_exemple)
        registre = db.notes.get_all()[0]
        assert registre == Note(id=1,student_id=1,category_id=1,date='2026-01-01',course_id=1,content='Anotació exemple')
        assert db.academic_courses.get_by_id(registre.course_id) == AcademicCourse(1,"2025-2026")


    def test_creacio_contactes(self,db):
        """Verifica la creació d'un contacte d'alumne"""
        contacte_exemple = ContactNew(1,"Joan","Pare","999999999","correu@example.com")
        db.contacts.create(contacte_exemple)
        registre_contactes = db.contacts.get_by_student(1)[0]
        assert registre_contactes == Contact(1,1,'Joan','Pare','999999999','correu@example.com')

    def test_creacio_anotacions(self,db):
        """Verifica la creació d'una anotació sobre un alumne"""
        anotacio_exemple = StudentAnnotationNew(1,"Anotació prova")
        db.annotations.create(anotacio_exemple)
        registre_annotacions = db.annotations.get_by_student(1)[0]
        assert registre_annotacions == StudentAnnotation(1,1,'Anotació prova')


class TestUpdateRegisters:
    """Comprovació sobre actualitzacions de registres."""

    def test_categoria(self,db):
        """Comprova que les categories s'actualitzen correctament"""
        categoria_actualitzada = Category(1,'Acadèmic primària')
        db.categories.rename(categoria_actualitzada)
        assert db.categories.get_all()[0]== categoria_actualitzada

    def test_alumne(self,db):
        """Test per a comprovar que un alumne s'actualitza correctament"""
        uuid_alumne_test = db.students.get_by_id(1).uuid
        alumne_test_actualitzacio = Student(1,uuid_alumne_test, "Josep", "Garcia", "4t A")
        db.students.update(alumne_test_actualitzacio)
        assert db.students.get_all()[0] == Student(
            1,
            uuid_alumne_test,
            'Josep',
            'Garcia',
            '4t A',
        )
    
    def test_registres(self,db):
        """Test per a comprovar que els registres de les anotacion s'actualitzen correctament"""
        registre_actualitzat = Note(1,1,1,"2026-01-08",1,"Anotació exemple")
        db.notes.update(registre_actualitzat)
        assert db.notes.get_by_id(1) == registre_actualitzat

   
    def test_contactes(self,db):
        """Test en què s'actualitza el telèfon d'un contacte"""
        contacte_actualitzat = Contact(1,1,"Joan","Pare","999999998","correu@example.com")
        db.contacts.update(contacte_actualitzat)
        assert db.contacts.get_by_student(1)[0] == contacte_actualitzat

    def test_anotacions(self,db):
        """Test per a comprovar l'actualització dels descriptors d'alumnes"""
        anotacio_actualitzada = StudentAnnotation(1,1,"Anotació actualitzada")
        db.annotations.update(anotacio_actualitzada)
        assert db.annotations.get_by_student(1)[0]==anotacio_actualitzada

class TestReadingOperations:

    def test_lectura_categories(self,db):
        """Testeig de les operacions de lectura de les categories"""
        categories_registrades=db.categories.get_by_name("Acadèmic primària")
        assert categories_registrades == Category(1,'Acadèmic primària')

    def test_lectura_cursos_academics(self,db):
        """Testeig de les operacions de lectura dels cursos"""
        cursos_registrats_general = db.academic_courses.get_all()
        curs_individual_id=db.academic_courses.get_by_id(1)
        curs_individual_text = db.academic_courses.get_by_course("2025-2026")
        nou_curs = AcademicCourse(2,'2026-2027')
        assert isinstance(cursos_registrats_general,list) is True
        assert curs_individual_id == AcademicCourse(1,"2025-2026")
        assert curs_individual_text == AcademicCourse(1,"2025-2026")
        assert db.academic_courses.get_or_create("2026-2027") == nou_curs

    def test_lectura_alumne(self,db):
        alumne_cerca = Student(1,db.students.get_by_id(1).uuid,"Josep", "Garcia","4t A")
        assert db.students.search("Josep")[0] == alumne_cerca
        assert db.students.get_by_full_name("Josep","Garcia","4t A") == alumne_cerca
        assert db.students.get_by_id(1) == alumne_cerca
        assert db.students.get_groups()[0] == '4t A'

    def test_lectura_anotacions(self,db):
        alumne_cerca = Student(1,db.students.get_by_id(1).uuid,"Josep", "Garcia","4t A")
        nota_registrada = Note(1,1,1,"2026-01-08",1,"Anotació exemple")
        registre_combinat=NoteRecord(1,'2026-01-08','Josep Garcia','4t A','Acadèmic primària','Anotació exemple',1,1)
        assert db.notes.get_by_student(alumne_cerca.id)[0] == nota_registrada
        assert db.notes.exists(alumne_cerca.id,nota_registrada.category_id,'2026-01-08','Anotació exemple') is True
        assert db.notes.get_records()[0]== registre_combinat

class TestDeleting:
    """Verifica les operacions d'eliminiació"""
    
    def test_categories_amb_registres(self,db):
        """Verifica que es genera un error si s'intenten esborrar categories associades a registres"""
        with pytest.raises(ValueError):
            db.categories.delete(1)


    def test_delete_notes(self,db):
        """Verifica que els registres s'eliminen correctament"""
        db.notes.delete(1)
        assert db.notes.get_all()== []

    def test_delete_categories(self,db):
        """Verifica que les categories s'eliminen correctament"""
        db.categories.delete(1)
        assert db.categories.get_all() == []

    def test_delete_annotations(self,db):
        """Verifica que les anotacions s'eliminen correctament"""
        db.annotations.delete(1)
        assert db.annotations.get_by_student(1) == []

    def test_delete_contacts(self,db):
        """Verifica que els contactes s'eliminen correctament"""
        db.contacts.delete(1)
        assert db.contacts.get_by_student(1) == []

    def test_delete_courses(self,db):
        """Verifica que els cursos s'eliminen correctament"""
        db.academic_courses.delete(1)
        assert db.academic_courses.get_by_id(1) is None

    def test_delete_students(self,db):
        """Verifica que els estudiants s'eliminen correctament"""
        db.students.delete(1)
        assert db.students.get_by_id(1) is None
