import pytest
from tutopy.entities.user import Category, Student, Note, NoteRecord

class Test_categories():

    def test_blanc(self, categoria_dataclass):
        exemple = categoria_dataclass
        assert exemple.id == 1
        assert exemple.name == "prova"
        

    def test_error_parametres(self):
        with pytest.raises(ValueError):
            exemple_2=Category(id="a",name=2)

class Test_estudiants():

    def test_blanc(self, estudiant_dataclass):
        alumne_exemple = estudiant_dataclass
        assert alumne_exemple.id == 1
        assert alumne_exemple.first_name == "primer cognom"
        assert alumne_exemple.last_name == "segon cognom"
        assert alumne_exemple.group_name == "grup A"
        

    def test_error_parametres(self):
        with pytest.raises(ValueError):
            exemple_2=Student(id="a",first_name=2,last_name=3,group_name=4)


class Test_notes():

    def test_blanc(self, nota_dataclass):
        assert nota_dataclass.id == 1
        assert nota_dataclass.student_id == 1
        assert nota_dataclass.category_id == 1
        assert nota_dataclass.date == "2026-01-01"
        assert nota_dataclass.content == "un registre d'exemple"
        

    def test_error_parametres(self):
        with pytest.raises(ValueError):
            exemple_registre=Note(id="a",student_id="b",category_id="b",date=1,content=4)

    def test_format_data(self):
        with pytest.raises(ValueError):
            exemple_registre=Note(id=1,student_id=1,category_id=1,date="06-06-2026",content="a")

class Test_registres():

    def test_blanc(self, notes_dataclass):
        assert notes_dataclass.note_id == 1
        assert notes_dataclass.date == "2026-01-01"
        assert notes_dataclass.student_name == "Pep"
        assert notes_dataclass.group_name == "A"
        assert notes_dataclass.category_name == "Acadèmic"
        assert notes_dataclass.content == "un registre d'exemple"
        assert notes_dataclass.student_id == 1
        assert notes_dataclass.category_id == 1
        

    def test_error_parametres(self):
        with pytest.raises(ValueError):
            exemple_registre=Note(id="a",student_id="b",category_id="b",date=1,content=4)

    def test_format_data(self):
        with pytest.raises(ValueError):
            exemple_registre=NoteRecord(note_id=1,date="06-06-2026",student_name="Jordi",group_name="B",category_name="Discilplina",content="Hola",student_id=1,category_id=1)
