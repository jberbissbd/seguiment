from pathlib import Path
import sqlite3
import uuid, pytest
from tutopy.models.messaging import (
    CategoryNew, Category, 
    AcademicCourse, AcademicCourseNew, 
    Student, StudentNew, 
    Note, NoteNew, NoteRecord, 
    ContactNew, Contact, 
    StudentAnnotation, StudentAnnotationNew,
    StudentDocument, StudentDocumentNew,
    StudentPhoto,
)
from tutopy.models.classroom_layout import CellType, ClassroomLayoutNew, LayoutCell
from tutopy.database.database import Database


def test_database_assigna_la_versio_actual_de_l_esquema(db):
    version = db.conn.execute("PRAGMA user_version").fetchone()[0]

    assert version == Database.SCHEMA_VERSION


def test_database_rebutja_un_esquema_mes_nou(tmp_path):
    path = tmp_path / "future.db"
    connection = sqlite3.connect(path)
    connection.execute(f"PRAGMA user_version = {Database.SCHEMA_VERSION + 1}")
    connection.close()

    database = Database(str(path))
    with pytest.raises(RuntimeError, match="versió més nova"):
        database.connect()

    assert database.conn is None


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

    def test_creacio_taula_student_photos(self, db):
        """Comprova que s'ha creat la taula student_photos"""
        nom_taula = 'student_photos'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_classroom_layouts(self, db):
        """Comprova que s'ha creat la taula classroom_layouts"""
        nom_taula = 'classroom_layouts'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1

    def test_creacio_taula_classroom_layout_cells(self, db):
        """Comprova que s'ha creat la taula classroom_layout_cells"""
        nom_taula = 'classroom_layout_cells'
        instruccio = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nom_taula}'"
        assert db.conn.execute(instruccio).fetchone()[0] == 1


class TestCreateRegisters:
    """Testeja la creació de registres a les taules"""

    def test_creacio_registre_categoria(self, db):
        """Verifica la creació d'un sol registre de la taula de categories"""
        categoria_test_individual = CategoryNew("Acadèmic")
        cat = db.categories.create(categoria_test_individual)
        assert db.categories.get_all()[0] == Category(cat.id, 'Acadèmic')

    def test_creacio_registre_cursacademic(self, db):
        """Verifica la creació d'un sol registre de la taula de cursos acadèmics"""
        curs_test_individual = AcademicCourseNew("2025-2026")
        course = db.academic_courses.create(curs_test_individual)
        assert db.academic_courses.get_all()[0] == AcademicCourse(course.id, '2025-2026')

    def test_creacio_registre_alumne(self, db):
        """Verifica la creació d'un sol registre de la taula d'alumnes"""
        uuid_alumne_test = str(uuid.uuid4())
        alumne_test_individual = StudentNew("Jordi", "Garcia", "4t A")
        alumne_creat = db.students.create(alumne_test_individual)
        assert db.students.get_all()[0] == Student(
            alumne_creat.id,
            alumne_creat.uuid,
            'Jordi',
            'Garcia',
            '4t A',
        )

    def test_creacio_registre_nota(self, db):
        """Verifica la creació d'una anotació"""
        # Crear dependencies: categoria, curs, alumne
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear la nota
        anotacio_exemple = NoteNew(alumne.id, categoria.id, "2026-01-01", curs.id, "Anotació exemple")
        registre = db.notes.create(anotacio_exemple)
        
        expected_note = Note(
            id=registre.id,
            student_id=alumne.id,
            category_id=categoria.id,
            date='2026-01-01',
            course_id=curs.id,
            content='Anotació exemple'
        )
        assert registre == expected_note
        assert db.academic_courses.get_by_id(registre.course_id) == AcademicCourse(curs.id, "2025-2026")

    def test_creacio_contactes(self, db):
        """Verifica la creació d'un contacte d'alumne"""
        # Crear alumne primer
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        contacte_exemple = ContactNew(alumne.id, "Joan", "Pare", "999999999", "correu@example.com")
        registre_contactes = db.contacts.create(contacte_exemple)
        
        assert registre_contactes == Contact(
            registre_contactes.id,
            alumne.id,
            'Joan',
            'Pare',
            '999999999',
            'correu@example.com'
        )

    def test_creacio_anotacions_alumne(self, db):
        """Verifica la creació d'una anotació sobre un alumne"""
        # Crear alumne primer
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        anotacio_exemple = StudentAnnotationNew(alumne.id, "Anotació prova")
        registre_annotacions = db.annotations.create(anotacio_exemple)
        
        assert registre_annotacions == StudentAnnotation(
            registre_annotacions.id,
            alumne.id,
            'Anotació prova'
        )


class TestUpdateRegisters:
    """Comprovació sobre actualitzacions de registres."""

    def test_categoria(self, db):
        """Comprova que les categories s'actualitzen correctament"""
        # Crear categoria primer
        cat = db.categories.create(CategoryNew("Acadèmic"))
        
        categoria_actualitzada = Category(cat.id, 'Acadèmic primària')
        db.categories.rename(categoria_actualitzada)
        assert db.categories.get_all()[0] == categoria_actualitzada

    def test_alumne(self, db):
        """Test per a comprovar que un alumne s'actualitza correctament"""
        # Crear alumne primer
        uuid_alumne_test = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        alumne_test_actualitzacio = Student(
            alumne.id,
            alumne.uuid,
            "Josep",
            "Garcia",
            "4t A"
        )
        db.students.update(alumne_test_actualitzacio)
        assert db.students.get_all()[0] == alumne_test_actualitzacio

    def test_registres_notes(self, db):
        """Test per a comprovar que els registres de les anotacions s'actualitzen correctament"""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        nota = db.notes.create(NoteNew(
            alumne.id,
            categoria.id,
            "2026-01-01",
            curs.id,
            "Anotació exemple"
        ))
        
        registre_actualitzat = Note(
            nota.id,
            alumne.id,
            categoria.id,
            "2026-01-08",
            curs.id,
            "Anotació exemple"
        )
        db.notes.update(registre_actualitzat)
        assert db.notes.get_by_id(nota.id) == registre_actualitzat

    def test_contactes(self, db):
        """Test en què s'actualitza el telèfon d'un contacte"""
        # Crear dependencies
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        contacte = db.contacts.create(ContactNew(
            alumne.id,
            "Joan",
            "Pare",
            "999999999",
            "correu@example.com"
        ))
        
        contacte_actualitzat = Contact(
            contacte.id,
            alumne.id,
            "Joan",
            "Pare",
            "999999998",
            "correu@example.com"
        )
        db.contacts.update(contacte_actualitzat)
        assert db.contacts.get_by_student(alumne.id)[0] == contacte_actualitzat

    def test_anotacions(self, db):
        """Test per a comprovar l'actualització dels descriptors d'alumnes"""
        # Crear dependencies
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        anotacio = db.annotations.create(StudentAnnotationNew(alumne.id, "Anotació prova"))
        
        anotacio_actualitzada = StudentAnnotation(
            anotacio.id,
            alumne.id,
            "Anotació actualitzada"
        )
        db.annotations.update(anotacio_actualitzada)
        assert db.annotations.get_by_student(alumne.id)[0] == anotacio_actualitzada


class TestReadingOperations:
    """Tests per operacions de lectura"""

    def test_lectura_categories(self, db):
        """Testeig de les operacions de lectura de les categories"""
        # Crear categoria
        cat = db.categories.create(CategoryNew("Acadèmic"))
        db.categories.rename(Category(cat.id, "Acadèmic primària"))
        
        categories_registrades = db.categories.get_by_name("Acadèmic primària")
        assert categories_registrades == Category(cat.id, 'Acadèmic primària')

    def test_lectura_cursos_academics(self, db):
        """Testeig de les operacions de lectura dels cursos"""
        # Crear curs existent
        curs_existent = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        cursos_registrats_general = db.academic_courses.get_all()
        curs_individual_id = db.academic_courses.get_by_id(curs_existent.id)
        curs_individual_text = db.academic_courses.get_by_course("2025-2026")
        nou_curs = AcademicCourse(curs_existent.id + 1, '2026-2027')
        
        assert isinstance(cursos_registrats_general, list) is True
        assert curs_individual_id == AcademicCourse(curs_existent.id, "2025-2026")
        assert curs_individual_text == AcademicCourse(curs_existent.id, "2025-2026")
        assert db.academic_courses.get_or_create("2026-2027") == nou_curs

    def test_lectura_alumne(self, db):
        """Testeig de les operacions de lectura d'alumnes"""
        # Crear alumne
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Josep", "Garcia", "4t A"))
        
        alumne_cerca = Student(alumne.id, alumne.uuid, "Josep", "Garcia", "4t A")
        assert db.students.search("Josep")[0] == alumne_cerca
        assert db.students.get_by_full_name("Josep", "Garcia", "4t A") == alumne_cerca
        assert db.students.get_by_id(alumne.id) == alumne_cerca
        assert db.students.get_groups()[0] == '4t A'

    def test_lectura_anotacions(self, db):
        """Testeig de les operacions de lectura d'anotacions"""
        # Crear dependencies
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        db.categories.rename(Category(categoria.id, "Acadèmic primària"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Josep", "Garcia", "4t A"))
        
        nota_registrada = db.notes.create(NoteNew(
            alumne.id,
            categoria.id,
            "2026-01-08",
            curs.id,
            "Anotació exemple"
        ))
        
        # Actualitzar la nota per tenir la data correcta
        nota_actualitzada = Note(
            nota_registrada.id,
            alumne.id,
            categoria.id,
            "2026-01-08",
            curs.id,
            "Anotació exemple"
        )
        db.notes.update(nota_actualitzada)
        
        registre_combinat = NoteRecord(
            nota_registrada.id,
            '2026-01-08',
            'Josep Garcia',
            '4t A',
            'Acadèmic primària',
            'Anotació exemple',
            categoria.id,
            curs.id
        )
        
        assert db.notes.get_by_student(alumne.id)[0] == nota_actualitzada
        assert db.notes.exists(
            alumne.id,
            categoria.id,
            '2026-01-08',
            'Anotació exemple'
        ) is True
        assert db.notes.get_records()[0] == registre_combinat


class TestDeleting:
    """Verifica les operacions d'eliminiació"""

    def test_categories_amb_registres(self, db):
        """Verifica que es genera un error si s'intenten esborrar categories associades a registres"""
        # Crear categoria i una nota que la fa servir
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear nota que usa aquesta categoria
        db.notes.create(NoteNew(
            alumne.id,
            categoria.id,
            "2026-01-01",
            curs.id,
            "Anotació exemple"
        ))
        
        # Ara intentem esborrar la categoria - hauria de fallar
        with pytest.raises(ValueError):
            db.categories.delete(categoria.id)

    def test_delete_notes(self, db):
        """Verifica que els registres de notes s'eliminen correctament"""
        # Crear dependencies i la nota
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        nota = db.notes.create(NoteNew(
            alumne.id,
            categoria.id,
            "2026-01-01",
            curs.id,
            "Anotació exemple"
        ))
        
        # Verificar que existeix
        assert len(db.notes.get_all()) == 1
        
        # Eliminar
        db.notes.delete(nota.id)
        assert db.notes.get_all() == []

    def test_delete_categories(self, db):
        """Verifica que les categories sense registres associats s'eliminen correctament"""
        categoria = db.categories.create(CategoryNew("Acadèmic"))
        
        # Verificar que existeix
        assert len(db.categories.get_all()) == 1
        
        # Eliminar
        db.categories.delete(categoria.id)
        assert db.categories.get_all() == []

    def test_delete_annotations(self, db):
        """Verifica que les anotacions s'eliminen correctament"""
        # Crear dependencies
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        anotacio = db.annotations.create(StudentAnnotationNew(alumne.id, "Anotació prova"))
        
        # Verificar que existeix
        assert len(db.annotations.get_by_student(alumne.id)) == 1
        
        # Eliminar
        db.annotations.delete(anotacio.id)
        assert db.annotations.get_by_student(alumne.id) == []

    def test_delete_contacts(self, db):
        """Verifica que els contactes s'eliminen correctament"""
        # Crear dependencies
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        contacte = db.contacts.create(ContactNew(
            alumne.id,
            "Joan",
            "Pare",
            "999999999",
            "correu@example.com"
        ))
        
        # Verificar que existeix
        assert len(db.contacts.get_by_student(alumne.id)) == 1
        
        # Eliminar
        db.contacts.delete(contacte.id)
        assert db.contacts.get_by_student(alumne.id) == []

    def test_delete_courses(self, db):
        """Verifica que els cursos s'eliminen correctament"""
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        # Verificar que existeix
        assert db.academic_courses.get_by_id(curs.id) == AcademicCourse(curs.id, "2025-2026")
        
        # Eliminar
        db.academic_courses.delete(curs.id)
        assert db.academic_courses.get_by_id(curs.id) is None

    def test_delete_students(self, db):
        """Verifica que els estudiants s'eliminen correctament"""
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Verificar que existeix
        assert db.students.get_by_id(alumne.id) is not None
        
        # Eliminar
        db.students.delete(alumne.id)
        assert db.students.get_by_id(alumne.id) is None

    def test_is_deletable_with_no_dependencies(self, db):
        """Verifica que is_deletable retorna True per categories sense notes associades"""
        categoria = db.categories.create(CategoryNew("Esport"))
        assert db.categories.is_deletable(categoria.id) is True

    def test_is_deletable_with_dependencies(self, db):
        """Verifica que is_deletable retorna False per categories amb notes associades"""
        categoria = db.categories.create(CategoryNew("Esport"))
        curs = db.academic_courses.create(AcademicCourseNew("2025-2026"))
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        # Crear una nota que usa aquesta categoria
        db.notes.create(NoteNew(
            alumne.id,
            categoria.id,
            "2026-01-01",
            curs.id,
            "Anotació exemple"
        ))
        
        assert db.categories.is_deletable(categoria.id) is False


class TestDocumentOperations:
    """Tests per operacions amb documents d'estudiants"""

    def test_get_all_empty(self, db):
        """Test que get_all retorna lista buida quan no hi ha documents"""
        assert db.documents.get_all() == []

    def test_create_document(self, db):
        """Verifica la creació d'un document d'estudiant"""
        # Crear alumne primer
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        doc_data = StudentDocumentNew(
            student_id=alumne.id,
            name="Document de prova",
            description="Descripció del document",
            uuid_filename=str(uuid.uuid4()),
            original_filename="document.pdf",
            file_path="/path/to/document.pdf"
        )
        doc = db.documents.create(doc_data)
        
        assert doc.id is not None
        assert doc.student_id == alumne.id
        assert doc.name == "Document de prova"
        assert doc.description == "Descripció del document"
        assert doc.uuid_filename == doc_data.uuid_filename
        assert doc.original_filename == "document.pdf"
        assert doc.file_path == "/path/to/document.pdf"

    def test_get_by_id(self, db):
        """Verifica la lectura d'un document per ID"""
        # Crear document
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        doc = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document test",
            description="Desc",
            uuid_filename=str(uuid.uuid4()),
            original_filename="test.txt",
            file_path="/path/test.txt"
        ))
        
        # Obtenir per ID
        retrieved = db.documents.get_by_id(doc.id)
        assert retrieved is not None
        assert retrieved.id == doc.id
        assert retrieved.name == "Document test"

    def test_get_by_id_nonexistent(self, db):
        """Verifica que get_by_id retorna None per ID inexistent"""
        assert db.documents.get_by_id(99999) is None

    def test_get_by_student(self, db):
        """Verifica la lectura de documents per estudiant"""
        # Crear alumne i documents
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        
        doc1 = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document 1",
            description="Desc 1",
            uuid_filename=str(uuid.uuid4()),
            original_filename="doc1.pdf",
            file_path="/path/doc1.pdf"
        ))
        doc2 = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document 2",
            description="Desc 2",
            uuid_filename=str(uuid.uuid4()),
            original_filename="doc2.pdf",
            file_path="/path/doc2.pdf"
        ))
        
        student_docs = db.documents.get_by_student(alumne.id)
        assert len(student_docs) == 2
        assert all(d.student_id == alumne.id for d in student_docs)

    def test_get_by_student_empty(self, db):
        """Test que get_by_student retorna lista buida quan l'estudiant no té documents"""
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        assert db.documents.get_by_student(alumne.id) == []

    def test_update_document(self, db):
        """Verifica l'actualització d'un document"""
        # Crear document
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        doc = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document vell",
            description="Descripció vella",
            uuid_filename=str(uuid.uuid4()),
            original_filename="vell.txt",
            file_path="/path/vell.txt"
        ))
        
        # Actualitzar (només name i description, según el DAO)
        updated_doc = StudentDocument(
            id=doc.id,
            student_id=alumne.id,
            name="Document nou",
            description="Descripció nova",
            uuid_filename=doc.uuid_filename,
            original_filename=doc.original_filename,
            file_path=doc.file_path
        )
        db.documents.update(updated_doc)
        
        # Verificar
        retrieved = db.documents.get_by_id(doc.id)
        assert retrieved.name == "Document nou"
        assert retrieved.description == "Descripció nova"
        # file_path no s'actualitza segons el DAO, així que ha de romandre igual
        assert retrieved.file_path == doc.file_path

    def test_delete_document(self, db):
        """Verifica l'eliminació d'un document"""
        # Crear document
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        doc = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document a esborrar",
            description="Desc",
            uuid_filename=str(uuid.uuid4()),
            original_filename="esborrar.txt",
            file_path="/path/esborrar.txt"
        ))
        
        # Verificar que existeix
        assert db.documents.get_by_id(doc.id) is not None
        assert len(db.documents.get_all()) == 1
        
        # Eliminar
        db.documents.delete(doc.id)
        assert db.documents.get_by_id(doc.id) is None
        assert db.documents.get_all() == []

    def test_delete_document_cascades(self, db):
        """Verifica que l'eliminació d'un alumne elimina els seus documents (CASCADE)"""
        # Crear alumne i document
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        doc = db.documents.create(StudentDocumentNew(
            student_id=alumne.id,
            name="Document",
            description="Desc",
            uuid_filename=str(uuid.uuid4()),
            original_filename="doc.txt",
            file_path="/path/doc.txt"
        ))
        
        # Verificar que el document existeix
        assert db.documents.get_by_id(doc.id) is not None
        
        # Eliminar l'alumne (ha d'eliminar el document per CASCADE)
        db.students.delete(alumne.id)
        
        # Verificar que el document també s'ha eliminat
        assert db.documents.get_by_id(doc.id) is None


class TestPhotoOperations:
    """Tests per operacions amb la foto de perfil dels alumnes"""

    def test_get_by_student_sense_foto(self, db):
        """Verifica que get_by_student retorna None si l'alumne no té foto"""
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        assert db.photos.get_by_student(alumne.id) is None

    def test_set_crea_la_foto(self, db):
        """Verifica que set() crea la foto d'un alumne"""
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        photo = db.photos.set(StudentPhoto(
            student_id=alumne.id, uuid_filename="foto.png",
            original_filename="original.png", file_path="/path/foto.png",
        ))
        assert photo.student_id == alumne.id
        retrieved = db.photos.get_by_student(alumne.id)
        assert retrieved.file_path == "/path/foto.png"

    def test_set_substitueix_la_foto_existent(self, db):
        """Verifica que set() sobre un alumne amb foto la substitueix (upsert)"""
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.photos.set(StudentPhoto(alumne.id, "vella.png", "a.png", "/path/vella.png"))
        db.photos.set(StudentPhoto(alumne.id, "nova.png", "b.png", "/path/nova.png"))
        assert len(db.photos.get_all()) == 1
        assert db.photos.get_by_student(alumne.id).file_path == "/path/nova.png"

    def test_delete(self, db):
        """Verifica l'eliminació de la foto d'un alumne"""
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.photos.set(StudentPhoto(alumne.id, "foto.png", "a.png", "/path/foto.png"))
        db.photos.delete(alumne.id)
        assert db.photos.get_by_student(alumne.id) is None

    def test_get_by_students_inclou_alumnes_sense_foto(self, db):
        """Verifica que get_by_students retorna None per als alumnes sense foto"""
        amb_foto = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        sense_foto = db.students.create(StudentNew("Laia", "Serra", "4t A"))
        db.photos.set(StudentPhoto(amb_foto.id, "foto.png", "a.png", "/path/foto.png"))
        result = db.photos.get_by_students([amb_foto.id, sense_foto.id])
        assert result[amb_foto.id].file_path == "/path/foto.png"
        assert result[sense_foto.id] is None

    def test_delete_photo_cascades(self, db):
        """Verifica que l'eliminació d'un alumne elimina la seva foto (CASCADE)"""
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.photos.set(StudentPhoto(alumne.id, "foto.png", "a.png", "/path/foto.png"))
        db.students.delete(alumne.id)
        assert db.photos.get_by_student(alumne.id) is None


class TestClassroomLayoutOperations:
    """Tests per operacions amb les distribucions de taules d'aula"""

    def test_create_i_get_by_id(self, db):
        """Verifica la creació d'una distribució"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "1r trimestre", 3, 4), "2026-01-10",
        )
        assert layout.id is not None
        assert layout.group_name == "4t A"
        assert layout.rows == 3 and layout.columns == 4
        assert layout.teacher_mode == "strip"
        assert layout.is_active is False
        assert db.classroom_layouts.get_by_id(layout.id) == layout

    def test_get_by_group(self, db):
        """Verifica que get_by_group només retorna les distribucions del grup"""
        db.classroom_layouts.create(ClassroomLayoutNew("4t A", "A1", 3, 4), "2026-01-10")
        db.classroom_layouts.create(ClassroomLayoutNew("4t B", "B1", 3, 4), "2026-01-10")
        results = db.classroom_layouts.get_by_group("4t A")
        assert len(results) == 1
        assert results[0].name == "A1"

    def test_update_actualitza_metadades(self, db):
        """Verifica l'actualització de les metadades d'una distribució"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "A1", 3, 4), "2026-01-10",
        )
        from dataclasses import replace
        updated = replace(layout, name="A1 revisada", rows=5, columns=5)
        db.classroom_layouts.update(updated, "2026-02-01")
        reloaded = db.classroom_layouts.get_by_id(layout.id)
        assert reloaded.name == "A1 revisada"
        assert reloaded.rows == 5 and reloaded.columns == 5
        assert reloaded.updated_at == "2026-02-01"

    def test_delete(self, db):
        """Verifica l'eliminació d'una distribució"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "A1", 3, 4), "2026-01-10",
        )
        db.classroom_layouts.delete(layout.id)
        assert db.classroom_layouts.get_by_id(layout.id) is None

    def test_set_active_desmarca_l_anterior(self, db):
        """Verifica que set_active només deixa una distribució activa per grup"""
        first = db.classroom_layouts.create(ClassroomLayoutNew("4t A", "A1", 3, 4), "2026-01-10")
        second = db.classroom_layouts.create(ClassroomLayoutNew("4t A", "A2", 3, 4), "2026-01-10")
        db.classroom_layouts.set_active(first.id, "4t A")
        db.classroom_layouts.set_active(second.id, "4t A")
        assert db.classroom_layouts.get_active("4t A").id == second.id
        assert db.classroom_layouts.get_by_id(first.id).is_active is False

    def test_replace_cells_substitueix_totes_les_cel_les(self, db):
        """Verifica que replace_cells esborra i torna a inserir les cel·les"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "A1", 2, 2), "2026-01-10",
        )
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.classroom_layouts.replace_cells(layout.id, [
            LayoutCell(0, 0, CellType.SEAT, None, alumne.id),
            LayoutCell(0, 1, CellType.AISLE),
        ])
        cells = db.classroom_layouts.get_cells(layout.id)
        assert len(cells) == 2
        by_position = {(cell.row, cell.column): cell for cell in cells}
        assert by_position[(0, 0)].student_id == alumne.id
        assert by_position[(0, 1)].cell_type == CellType.AISLE

        db.classroom_layouts.replace_cells(layout.id, [
            LayoutCell(1, 1, CellType.TEACHER),
        ])
        cells = db.classroom_layouts.get_cells(layout.id)
        assert len(cells) == 1
        assert cells[0].row == 1 and cells[0].column == 1

    def test_delete_cascades_cel_les(self, db):
        """Verifica que l'eliminació d'una distribució esborra les seves cel·les"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "A1", 2, 2), "2026-01-10",
        )
        db.classroom_layouts.replace_cells(layout.id, [LayoutCell(0, 0, CellType.SEAT)])
        db.classroom_layouts.delete(layout.id)
        assert db.conn.execute(
            "SELECT count(*) FROM classroom_layout_cells WHERE layout_id = ?", (layout.id,),
        ).fetchone()[0] == 0

    def test_cella_oblida_l_alumne_en_eliminar_lo(self, db):
        """Verifica que eliminar un alumne buida la seva cel·la (SET NULL)"""
        layout = db.classroom_layouts.create(
            ClassroomLayoutNew("4t A", "A1", 2, 2), "2026-01-10",
        )
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        db.classroom_layouts.replace_cells(
            layout.id, [LayoutCell(0, 0, CellType.SEAT, None, alumne.id)],
        )
        db.students.delete(alumne.id)
        cells = db.classroom_layouts.get_cells(layout.id)
        assert cells[0].student_id is None

    def test_index_actiu_unic_rebutja_dues_actives_pel_mateix_grup(self, db):
        """Verifica que l'índex únic impedeix dues distribucions actives pel mateix grup"""
        import sqlite3
        first = db.classroom_layouts.create(ClassroomLayoutNew("4t A", "A1", 3, 4), "2026-01-10")
        second = db.classroom_layouts.create(ClassroomLayoutNew("4t A", "A2", 3, 4), "2026-01-10")
        db.conn.execute(
            "UPDATE classroom_layouts SET is_active = 1 WHERE id = ?", (first.id,),
        )
        db.conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            db.conn.execute(
                "UPDATE classroom_layouts SET is_active = 1 WHERE id = ?", (second.id,),
            )


class TestEdgeCases:
    """Tests per casos límit i escenaris especials"""

    def test_get_by_id_nonexistent_category(self, db):
        """Verifica que get_by_id retorna None per categoria inexistent"""
        assert db.categories.get_by_name("No existeix") is None

    def test_get_by_id_nonexistent_academic_course(self, db):
        """Verifica que get_by_id retorna None per curs inexistent"""
        assert db.academic_courses.get_by_id(99999) is None
        assert db.academic_courses.get_by_course("2999-3000") is None

    def test_get_all_empty_categories(self, db):
        """Test que get_all retorna lista buida quan no hi ha categories"""
        assert db.categories.get_all() == []

    def test_get_all_empty_students(self, db):
        """Test que get_all retorna lista buida quan no hi ha alumnes"""
        assert db.students.get_all() == []

    def test_get_all_empty_notes(self, db):
        """Test que get_all retorna lista buida quan no hi ha notes"""
        assert db.notes.get_all() == []

    def test_get_all_empty_contacts(self, db):
        """Test que get_by_student retorna lista buida per alumne sense contactes"""
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        assert db.contacts.get_by_student(alumne.id) == []

    def test_get_all_empty_annotations(self, db):
        """Test que get_by_student retorna lista buida per alumne sense anotacions"""
        uuid_alumne = str(uuid.uuid4())
        alumne = db.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        assert db.annotations.get_by_student(alumne.id) == []

    def test_search_no_results(self, db):
        """Test que search retorna lista buida quan no hi ha resultats"""
        assert db.students.search("No existeix") == []

    def test_get_groups_empty(self, db):
        """Test que get_groups retorna lista buida quan no hi ha grups"""
        assert db.students.get_groups() == []

    def test_category_unique_constraint(self, db):
        """Verifica que no es poden crear categories amb noms duplicats"""
        # Crear primera categoria
        db.categories.create(CategoryNew("Acadèmic"))
        
        # Intentar crear una altra amb el mateix nom - hauria de fallar
        duplicate = CategoryNew("Acadèmic")
        with pytest.raises(sqlite3.IntegrityError):
            db.categories.create(duplicate)

    def test_academic_course_unique_constraint(self, db):
        """Verifica que no es poden crear cursos acadèmics duplicats"""
        # Crear primer curs
        db.academic_courses.create(AcademicCourseNew("2025-2026"))
        
        # Intentar crear un altre amb el mateix nom - hauria de fallar
        duplicate = AcademicCourseNew("2025-2026")
        with pytest.raises(sqlite3.IntegrityError):
            db.academic_courses.create(duplicate)


def test_transaccio_exterior_agrupa_commits_dels_daos(db):
    """Una unitat de negoci massiva genera un únic COMMIT físic."""
    statements = []
    db.conn._connection.set_trace_callback(statements.append)

    with db.transaction():
        db.categories.create(CategoryNew("Acadèmic"))
        db.categories.create(CategoryNew("Família"))
        db.categories.create(CategoryNew("Orientació"))

    transaction_statements = [
        statement.strip().upper() for statement in statements
        if statement.strip().upper() in {"BEGIN", "COMMIT"}
    ]
    assert transaction_statements == ["BEGIN", "COMMIT"]


def test_transaccio_niuada_desfa_nomes_els_canvis_interiors(db):
    with db.transaction():
        db.categories.create(CategoryNew("Exterior abans"))
        try:
            with db.transaction():
                db.categories.create(CategoryNew("Interior"))
                raise RuntimeError("error interior")
        except RuntimeError:
            pass
        db.categories.create(CategoryNew("Exterior després"))

    assert [category.name for category in db.categories.get_all()] == [
        "Exterior abans", "Exterior després",
    ]


def test_rollback_exterior_desfa_savepoints_ja_confirmats(db):
    def commit_and_fail() -> None:
        with db.transaction():
            db.categories.create(CategoryNew("Exterior"))
            with db.transaction():
                db.categories.create(CategoryNew("Interior confirmat"))
            raise RuntimeError("error exterior")

    with pytest.raises(RuntimeError, match="error exterior"):
        commit_and_fail()

    assert db.categories.get_all() == []
