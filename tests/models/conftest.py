"""Fixtures compartides pels tests dels models de domini."""

import pytest
import uuid
from tutopy.models.messaging import AcademicCourse, AcademicCourseNew, Category, Student, StudentNew, Note, NoteRecord, Contact


@pytest.fixture(scope='module')
def categoria_dataclass():
    """Categoria d'exemple, ja existent."""
    categoria_prova = Category(1,"prova")
    return categoria_prova

@pytest.fixture(scope='module')
def uuid_test():
    """UUID d'exemple per a un estudiant nou."""
    uuid_prova = str(uuid.uuid4())
    return uuid_prova


@pytest.fixture(scope='module')
def curs_existent_dataclass():
    """Curs acadèmic d'exemple, ja existent."""
    curs_prova = AcademicCourse(id=1,course="2026-2027")
    return curs_prova

@pytest.fixture(scope='module')
def curs_nou_dataclass():
    """Curs acadèmic d'exemple, encara per crear."""
    curs_nou_prova= AcademicCourseNew("2026-2027")
    return curs_nou_prova


@pytest.fixture(scope='module')
def estudiant_existent_dataclass():
    """Estudiant d'exemple, ja existent."""
    estudiant_prova = Student(1,"a","Toni","Cognom 1 Cognom 2","grup A")
    return estudiant_prova

@pytest.fixture(scope='module')
def estudiant_nou_dataclass(uuid_test):
    """Fixture per a estudiants nous."""
    estudiant_prova = StudentNew("Toni", "Cognom 1 Cognom 2", "grup A")
    return estudiant_prova

@pytest.fixture(scope='module')
def nota_dataclass():
    """Nota de seguiment d'exemple, ja existent."""
    registre_prova = Note(1,1,1,"2026-01-01",1,"un registre d'exemple")
    return registre_prova

@pytest.fixture(scope='module')
def notes_dataclass():
    """Registre combinat d'exemple (nota amb alumne, grup i categoria resolts)."""
    registres_prova = NoteRecord(1,"2026-01-01","Pep","A","Acadèmic","un registre d'exemple",1,1)
    return registres_prova

@pytest.fixture(scope='module')
def contacte_dataclass():
    """Contacte d'exemple, ja existent."""
    contacte_prova = Contact(1,1,"Pep","Pare","999111222","something@company.com")
    return contacte_prova
