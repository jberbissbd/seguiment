import pytest
from tutopy.models.messaging import Category,CategoryNew, Student, StudentNew, Note, NoteNew, NoteRecord, Contact, ContactNew, StudentAnnotation, StudentAnnotationNew,AcademicCourse, AcademicCourseNew

class TestCategories():
    """Tests de categoríes"""

    def test_blanc(self, categoria_dataclass):
        """Comprova que una 'Category' es crea correctament"""
        exemple = categoria_dataclass
        assert exemple.id == 1
        assert exemple.name == "prova"


    def test_error_parametres__categoria_existent(self):
        """Comprova que genera un error al intentar crear una categoria amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_2=Category(id="a",name=2)


    def test_error_parametres__categoria_nova(self):
        """Comprova que genera un error al intentar crear una categoria amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_2=CategoryNew(name=2)

class TestCursosAcademics():
    """Tests relacionats als cursos acadèmics"""
    def test_blanc_existent(self,curs_existent_dataclass):
        assert curs_existent_dataclass.id == 1
        assert curs_existent_dataclass.course == "2026-2027"

    def test_blanc_nou(self,curs_nou_dataclass):
        """Testeig de la classe AcademicCourseNew"""
        assert curs_nou_dataclass.course == "2026-2027"

    def test_error_existent(self):
        """Comprova que genera en error quan s'intenta crear amb tipologies de dades incrrectes"""
        with pytest.raises(ValueError):
            exemple_curs = AcademicCourse(id="a",course=5)

    def test_error_nou(self):
        """Comprova que genera en error quan s'intenta crear amb tipologies de dades incrrectes"""
        with pytest.raises(ValueError):
            exemple_curs_2 = AcademicCourseNew(course=5)


class TestEstudiants():
    """Col·lecció de tests per a estudiants"""

    def test_blanc(self, estudiant_existent_dataclass):
        """Comprova els valors d'un Student per verificar que s'ha creat correctament"""
        alumne_exemple = estudiant_existent_dataclass
        assert alumne_exemple.id == 1
        assert alumne_exemple.uuid == "a"
        assert alumne_exemple.name == "Toni"
        assert alumne_exemple.surnames == "Cognom 1 Cognom 2"
        assert alumne_exemple.group_name == "grup A"


    def test_blanc_nou(self, estudiant_nou_dataclass):
        """Comprova els valors d'un StudentNew per verificar que s'ha creat correctament"""
        alumne_exemple = estudiant_nou_dataclass
        assert alumne_exemple.name == "Toni"
        assert alumne_exemple.surnames == "Cognom 1 Cognom 2"
        assert alumne_exemple.group_name == "grup A"


    def test_nom_complet(self,estudiant_existent_dataclass):
        """Comprova que el nom complet es genera correctament"""
        assert estudiant_existent_dataclass.full_name == "Toni Cognom 1 Cognom 2"

    def test_error_parametres_existent(self):
        """Comprova que genera un error al intentar crear un estudiant amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_2=Student(id="a",uuid=5,name=2,surnames=3,group_name=4)

    def test_error_parametres_nou(self):
        """Comprova que genera un error al intentar crear un estudiant amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_3 = StudentNew(name=2, surnames=3, group_name=4)

    def test_student_new_no_accepta_uuid_extern(self):
        """L'UUID és intern i no forma part del contracte de creació."""
        with pytest.raises(TypeError):
            StudentNew(uuid="extern", name="Toni", surnames="Cognoms", group_name="A")


class TestRegistreIndividual():
    """Tests respecte als registres individuals"""

    def test_blanc(self, nota_dataclass):
        """Comprova els valors d'un Note per verificar que s'ha creat correctament"""
        assert nota_dataclass.id == 1
        assert nota_dataclass.student_id == 1
        assert nota_dataclass.category_id == 1
        assert nota_dataclass.date == "2026-01-01"
        assert nota_dataclass.course_id == 1
        assert nota_dataclass.content == "un registre d'exemple"


    def test_error_parametres_existent(self):
        """Comprova que genera un error al intentar crear un Note amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre = NoteNew(student_id="b", category_id="b", date=1, course_id="a", content=4)


    def test_error_parametres_nou(self):
        """Comprova que genera un error al intentar crear un Note amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre = Note(id="a", student_id="b", category_id="b", course_id="a", date=1, content=4)


    def test_format_data_existent(self):
        """Comprova que el camp de data tan sols admet una data convertible a format ISO
        >>>exemple_registre=Note(id=1,student_id=1,category_id=1,date="06-06-2026",content="a")
        Traceback(most recent call last:)
        ValueError
        """
        with pytest.raises(ValueError):
            exemple_registre = Note(id=1, student_id=1, category_id=1, date="06-06-2026", course_id=1, content="a")

    def test_format_data_nou(self):
        """Comprova que el camp de data tan sols admet una data convertible a format ISO
        >>>exemple_registre=Note(id=1,student_id=1,category_id=1,date="06-06-2026",content="a")
        Traceback(most recent call last:)
        ValueError
        """
        with pytest.raises(ValueError):
            exemple_registre = NoteNew(student_id=1, category_id=1, date="06-06-2026", course_id=1, content="a")


class TestRegistresCombinats():
    """Tests per als registres combinats"""

    def test_blanc(self, notes_dataclass):
        """Comprova els valors d'un NoteRecord per verificar que s'ha creat correctament"""
        assert notes_dataclass.note_id == 1
        assert notes_dataclass.date == "2026-01-01"
        assert notes_dataclass.student_name == "Pep"
        assert notes_dataclass.group_name == "A"
        assert notes_dataclass.category_name == "Acadèmic"
        assert notes_dataclass.content == "un registre d'exemple"
        assert notes_dataclass.student_id == 1
        assert notes_dataclass.category_id == 1


    def test_error_parametres(self):
        """Comprova que genera un error al intentar crear un NoteRecord amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre=NoteRecord(note_id="a",date=2,student_name=2,group_name=3,category_name=2,content=4,student_id="a",category_id="a")

    def test_format_data(self):
        """Comprova que el camp de data tan sols admet una data convertible a format ISO"""
        with pytest.raises(ValueError):
            exemple_registre=NoteRecord(note_id=1,date="06-06-2026",student_name="Jordi",group_name="B",category_name="Discilplina",content="Hola",student_id=1,category_id=1)


class TestContactes():
    """Tests per a la dataclass 'Contact'"""

    def test_blanc(self, contacte_dataclass):
        """Test que comprova que el contacte_dataclass es crea correctament"""
        assert contacte_dataclass.id == 1
        assert contacte_dataclass.student_id == 1
        assert contacte_dataclass.name == "Pep"
        assert contacte_dataclass.description == "Pare"
        assert contacte_dataclass.phone == "937982091"
        assert contacte_dataclass.email == "something@company.com"


    def test_error_parametres_existent(self):
        """Comprova que genera un error al intentar crear un Contacte amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre=Contact(id="a",student_id="b",name=2,description=2,phone=10,email=3)

    def test_error_parametres_nou(self):
        """Comprova que genera un error al intentar crear un Contacte amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre=ContactNew(student_id="b",name=2,description=2,phone=10,email=3)

class TestAnotations():

    def test_error_parametres_existent(self):
        """Comprova que genera un error al intentar crear un Contacte amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre=StudentAnnotation(id="a",student_id="b",content=3)

    def test_error_parametres_nou(self):
        """Comprova que genera un error al intentar crear un Contacte amb la tipologia de 
        valors incorrecta.
        """
        with pytest.raises(ValueError):
            exemple_registre=StudentAnnotationNew(student_id="b",content=3)
