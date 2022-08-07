import dataclasses
import sys
import unittest
import random
from faker import Faker

from faker.providers import person
from src.agents.formats import Registres_bbdd_nou, Registres_bbdd_comm, Alumne_nou, Alumne_comm, Categoria_comm, \
    Data_gui_comm
from src.agents.agents_bbdd import AlumnesBbdd, CategoriesBbdd, RegistresBbdd, ModelDao, DatesBbdd

fake = Faker()
alumnes = AlumnesBbdd()
categories = CategoriesBbdd()
registres = RegistresBbdd()
calendari = DatesBbdd()

alumnes.ruta_bbdd = "tests/bbdd_tests.db"
registres.ruta_bbdd = "tests/bbdd_tests.db"
categories.ruta_bbdd = "tests/bbdd_tests.db"


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
        id_alumne = random.randint(1, alumnes.test_llegir_alumnes())
        id_categoria = random.randint(1, categories.test_lectura_categories())
        data_registre = fake.date()
        descripcio_registre = fake.text()
        llista_registre = [Registres_bbdd_nou(id_alumne, id_categoria, data_registre, descripcio_registre)]
        resultat_crear_regitre = registres.crear_registre(llista_registre)
        assert resultat_crear_regitre == True, "Comprova si un registre amb el format Registre de missatgeria " \
                                               "s'introdueix "

    def test_entrada_taula_dates(self):
        data_ficticia = fake.date()
        resultat_registre_data = calendari.crear_data(data_ficticia)
        assert resultat_registre_data == True, "Comprovacio al crear una data nova"


class Test_lectura_dades_bbdd(unittest.TestCase):
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


class Test_lectura_dades_bbdd_formats_resposta(unittest.TestCase):
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


class Test_formats_tipus_variables(unittest.TestCase):
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
            assert isinstance(element, Data_gui_comm), "Data no te el format Data_gui_comm)"


if __name__ == "__main__":
    unittest.main()
    # print(alumnes.llegir_alumnes())
    # print(alumnes.eliminar_alumne(1))
    # print(alumnes.llegir_alumnes())
    # print(categories.consultar_camp("nom_categoria"))
    # print(categories.llegir_categories())
    # print(categories.registrar_categoria(nom_categoria="categoria_test"))
    # print(categories.llegir_categories())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres.registrar_registre(id_alumne=1, id_categoria=1, data_registre="2020-01-01"))
    # print(registres.llegir_registres())
    # print(registres.eliminar_registre(id_registre=1))
    # print(registres.llegir_registres())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres.consultar_camp("id_alumne"))
    # print(registres.llegir_registres())
    # print(registres
