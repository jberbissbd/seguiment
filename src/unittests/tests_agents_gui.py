import unittest

from faker import Faker
from src.agents.agents_bbdd import AlumnesBbdd, CategoriesBbdd, RegistresBbdd, ModelDao, DatesBbdd, AjudantDirectoris
from src.agents.agents_gui import Calendaritzador, CapEstudis, Comptable, Classificador

fake = Faker("es_CA")

registres = Comptable(modegui=2)


class TestLectura(unittest.TestCase):
    """Classe per a comprovar les operacions de lectura de dades"""

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        assert isinstance(lectura_registres, list) is True, "Comptable ha de proporcionar una llista"


if __name__ == '__main__':
    unittest.main()
