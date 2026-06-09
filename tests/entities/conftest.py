import pytest
from tutopy.entities.user import Category, Student, Note, NoteRecord



@pytest.fixture(scope='module')
def categoria_dataclass():
    categoria_prova = Category(1,"prova")
    return categoria_prova

@pytest.fixture(scope='module')
def estudiant_dataclass():
    estudiant_prova = Student(1,"primer cognom","segon cognom","grup A")
    return estudiant_prova

@pytest.fixture(scope='module')
def nota_dataclass():
    registre_prova = Note(1,1,1,"2026-01-01","un registre d'exemple")
    return registre_prova

@pytest.fixture(scope='module')
def notes_dataclass():
    registres_prova = NoteRecord(1,"2026-01-01","Pep","A","Acadèmic","un registre d'exemple",1,1)
    return registres_prova

