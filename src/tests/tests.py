import dataclasses
import sys
import unittest
import random
from faker import Faker

from faker.providers import person
from src.agents.formats import Registres_bbdd_nou, Registres_bbdd_comm, Alumne_nou, Alumne_comm, Categoria_comm, \
    Data_gui_comm, Data_nova
from src.agents.agents_bbdd import AlumnesBbdd, CategoriesBbdd, RegistresBbdd, ModelDao, DatesBbdd

fake = Faker()
alumnes = AlumnesBbdd()
categories = CategoriesBbdd()
registres = RegistresBbdd()
calendari = DatesBbdd()

alumnes.ruta_bbdd = "tests/bbdd_tests.db"
registres.ruta_bbdd = "tests/bbdd_tests.db"
categories.ruta_bbdd = "tests/bbdd_tests.db"
calendari.ruta_bbdd = "tests/bbdd_tests.db"


class Test_entrada_dades_bbdd(unittest.TestCase):
    def setUp(self) -> None:
        categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_alumnes(self):
        nom_registrar = person.BaseProvider("name")
        missatge_registrar = [Alumne_nou(nom_registrar)]
        resultat_registre = alumnes.registrar_alumne(missatge_registrar)
        assert not True != resultat_registre, "Error al introduir nous valors a la taula d'alumnes"

    def test_categories(self):
        categoria_registrar = fake.text()
        missatge_registrar = []
        resultat_categories = categories.crear_categoria(categoria_registrar)
        assert resultat_categories == True, "Error al introduir nous valors a la taula de categories"

    def test_registres(self):
        id_alumne = random.choice(alumnes.test_llegir_alumnes())
        id_categoria = random.choice(categories.test_lectura_categories())
        data_registre = fake.date()
        descripcio_registre = fake.text()
        llista_registre = [Registres_bbdd_nou(id_alumne, id_categoria, data_registre, descripcio_registre)]
        resultat_crear_regitre = registres.crear_registre(llista_registre)
        assert resultat_crear_regitre == True, "Comprova si un registre amb el format Registre de missatgeria " \
                                               "s'introdueix "

    def test_dates(self):
        data_ficticia = fake.date()
        resultat_registre_data = calendari.crear_data([Data_nova(data_ficticia)])
        assert resultat_registre_data == True, "Comprovacio al crear una data nova"


class Test_actualitzacio(unittest.TestCase):
    """Classe per a comprovar operacio d'actualitzar"""

    def setUp(self) -> None:
        categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_alumnes(self):
        id_alumne = random.choice(alumnes.test_llegir_alumnes())
        nom_registrar = person.BaseProvider("name")
        missatge_registrar = [Alumne_comm(id_alumne, nom_registrar)]
        resultat_registre = alumnes.actualitzar_alumne(missatge_registrar)
        assert not True != resultat_registre, "Error al introduir nous valors a la taula d'alumnes"

    def test_registres(self):
        id_registre = random.choice(registres.test_id_registre())
        id_alumne = random.choice(alumnes.test_llegir_alumnes())
        id_categoria = random.choice(categories.test_lectura_categories())
        data_registre = fake.date()
        descripcio_registre = fake.text()
        llista_actualitzar = [
            Registres_bbdd_comm(id_registre, id_alumne, id_categoria, data_registre, descripcio_registre)]
        resultat = registres.actualitzar_registre(llista_actualitzar)
        assert resultat == True, "Comprova si un registre amb el format Registre de missatgeria " \
                                 "s'introdueix "

    def test_categories(self):
        id_categoria = random.choice(categories.test_lectura_categories())
        categoria_registrar = fake.text()
        missatge_registrar = [Categoria_comm(id_categoria, categoria_registrar)]
        resultat_categories = categories.actualitzar_categoria(missatge_registrar)
        assert resultat_categories == True, "Error al introduir nous valors a la taula de categories"

    def test_dates(self):
        id_data = random.choice(calendari.test_dates())
        nova_data = fake.date()
        missatge_registrar = [Data_gui_comm(id_data, nova_data)]
        resultat_registre = calendari.actualitzar_data(missatge_registrar)
        assert True == resultat_registre, "Error al introduir nous valors a la taula de dates"


class Test_lectura(unittest.TestCase):

    def setUp(self) -> None:
        categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_lectura_registres(self):
        llista_registres = registres.lectura_registres()
        assert isinstance(llista_registres, list), "Resultats han de ser una llista"

    def test_lectura_alumnes(self):
        llista_registres = alumnes.llegir_alumnes()
        assert isinstance(llista_registres, list), "Resultats han de ser una llista"

    def test_lectura_categories(self):
        llista_registres = categories.lectura_categories()
        assert isinstance(llista_registres, list), "Resultats han de ser una llista"

    def test_format_individual_categories_variables(self):
        llista_registres = categories.lectura_categories()
        for element in llista_registres:
            nombre = element.id
            nom = element.nom
            assert isinstance(nombre, int), "Atribut id ha de ser un nombre"
            assert isinstance(nom, str), "Nom ha de ser un text"

    def test_lectura_dates(self):
        llista_registres = calendari.lectura_dates()
        assert isinstance(llista_registres, list), "Resultats han de ser una llista"


class Test_formats_resposta(unittest.TestCase):
    """Comprovacio que la resposta de la lectura de la base de dades segueixi els formats estblerts per a cada taula.."""

    def setUp(self) -> None:
        categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_registres(self):
        llista_registres = registres.lectura_registres()
        for element in llista_registres:
            assert isinstance(element, Registres_bbdd_comm), "Registre no te el format Registres_bbdd_comm"

    def test_alumnes(self):
        llista_registres = alumnes.llegir_alumnes()
        for element in llista_registres:
            assert isinstance(element, Alumne_comm), "Alumne no te el format Alumne_comm"

    def test_categories(self):
        llista_registres = categories.lectura_categories()
        for element in llista_registres:
            assert isinstance(element, Categoria_comm), "Categoria no te el format Categoria_comm"

    def test_dates(self):
        llista_registres = calendari.lectura_dates()
        for element in llista_registres:
            assert isinstance(element, Data_gui_comm), "Data no te el format Data_gui_comm)"


class Test_tipus_atributs(unittest.TestCase):
    """Test per a comprovar si tots els elements de la base de dades compleixen amb la missatgeria establerta"""

    def setUp(self) -> None:
        categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_format_individual__registres_variables(self):
        llista_registres = registres.lectura_registres()
        for element in llista_registres:
            num_referencia = element.id
            categoria = element.categoria
            data = element.data
            alumne = element.alumne
            descripcio = element.descripcio
            assert isinstance(num_referencia, int), "ID del registre ha de ser un numero"
            assert isinstance(alumne, int), "Alumne del registre ha de ser un numero"
            assert isinstance(categoria, int), "Categoria del registre ha de ser un numero"
            assert isinstance(data, str), "Data del registre ha de ser text"
            assert isinstance(descripcio, str), "Descripcio del registre ha de ser text"

    def test_alumnes(self):
        llista_registres = alumnes.llegir_alumnes()
        for element in llista_registres:
            nombre = element.id
            nom = element.nom
            assert isinstance(nombre, int), "Atribut id ha de ser un nombre"
            assert isinstance(nom, str), "Nom ha de ser un text"

    def test_categories(self):
        llista_registres = categories.lectura_categories()
        for element in llista_registres:
            nombre = element.id
            descripcio = element.nom
            assert isinstance(nombre, int), "L'ID ha de ser un nombre"
            assert isinstance(descripcio, str), "La descripcio ha de ser un text"

    def test_dates(self):
        llista_registres = calendari.lectura_dates()
        for element in llista_registres:
            nombre = element.id
            data = element.dia
            assert isinstance(nombre, int), "La referencia de la data ha de ser un nombre"
            assert isinstance(data, str), "La data ha de ser una cadena de text"


def bbdd_lectura():
    bbdd_operacions_lectura = unittest.TestSuite()
    bbdd_operacions_lectura.addTest(Test_lectura)
    bbdd_operacions_lectura.addTest(Test_formats_resposta)
    bbdd_operacions_lectura.addTest(Test_tipus_atributs)
    return bbdd_operacions_lectura


def bbdd_escriptura():
    escriptura = unittest.TestSuite()
    escriptura.addTest(Test_entrada_dades_bbdd)
    return escriptura

def bbdd_actualitzacio():
    actualitzacio = unittest.TestSuite
    actualitzacio.addTest(Test_actualitzacio)
    return actualitzacio

if __name__ == "__main__":
    executor = unittest.TextTestRunner()
    executor.run(bbdd_lectura())
    executor.run(bbdd_escriptura())
    executor.run(bbdd_actualitzacio())
