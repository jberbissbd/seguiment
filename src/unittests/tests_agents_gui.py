import unittest

from faker import Faker

from src.agents.agents_gui import Calendaritzador, CapEstudis, Comptable, Classificador

fake = Faker("es_CA")
alumnes = CapEstudis()
categories = Classificador()
registres = Comptable()
calendari = Calendaritzador()
ruta_base_dades = "/home/jordi/Documents/Projectes/seguiment/src/unittests/tests.db"

alumnes.ruta_bbdd = ruta_base_dades
registres.ruta_bbdd = ruta_base_dades
categories.ruta_bbdd = ruta_base_dades
calendari.ruta_bbdd = ruta_base_dades


class TestLectura(unittest.TestCase):
    """Classe per a comprovar les operacions de lectura de dades"""

    def setUp(self, db=ruta_base_dades) -> None:
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        assert isinstance(lectura_registres, list) is True, "Comptable ha de proporcionar una llista"


if __name__ == '__main__':
    unittest.main()
