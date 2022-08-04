import unittest
import random
from faker import Faker
from faker.providers import random
from src.agents.formats import Registres_bbdd_nou
from src.agents.agents_bbdd import AlumnesBbdd, CategoriesBbdd, RegistresBbdd, ModelDao, DatesBbdd

fake = Faker()
alumnes = AlumnesBbdd()
categories = CategoriesBbdd()
registres = RegistresBbdd()
calendari = DatesBbdd()

alumnes.ruta_bbdd = "tests/bbdd_tests.db"


class Test_entrada_dades(unittest.TestCase):
    categories.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
    registres.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
    alumnes.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
    calendari.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/tests/tests.db"
    categories.taula = "categories"
    registres.taula = "registres"
    alumnes.taula = "alumnes"
    calendari.taula = "dates"

    def test_alumnes(self):
        nom_registrar = fake.name()
        resultat_registre = alumnes.registrar_alumne(nom_registrar)
        assert not True != resultat_registre, "Error al introduir nous valors a la taula d'alumnes"

    def test_categories(self):
        categoria_registrar = fake.text()
        resultat_categories = categories.crear_categoria(categoria_registrar)
        assert resultat_categories == True, "Error al introduir nous valors a la taula de categories"

    def test_registres(self):
        id_alumne = random.randint(1, 18)
        id_categoria = random.randint(1, 2)
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


class Test_lectura_dades(unittest.TestCase):

    def lectura_registres(self):
        pass


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
