import sys
import unittest
sys.path.append('/home/jordi/Documents/Projectes/seguiment/src/agents')
from faker import Faker
from src.agents.agents_gui import Calendaritzador, CapEstudis, Comptable, Classificador

fake = Faker("es_CA")
error_lista = " .Error: ha de proporcionar una llista."

registres = Comptable(modegui=2)
alumnes = CapEstudis(modegui=2)
calendari = Calendaritzador(modegui=2)
classificador = Classificador(modegui=2)


class TestLectura(unittest.TestCase):
    """Classe per a comprovar les operacions de lectura de dades"""

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        assert isinstance(lectura_registres, list) is True, f"Classe Comptable{error_lista}"

    def test_alumnes(self):
        lectura_registres = alumnes.alumnat
        assert isinstance(lectura_registres, list) is True, f"Classe Cap d'Estudis{error_lista}"

    def test_alumnes_registres(self):
        lectura_registres = alumnes.alumnat_registres
        assert isinstance(lectura_registres, list) is True, f"Classe Cap d'Estudis{error_lista}"

    def test_dates(self):
        lectura_registres = calendari.dates
        assert isinstance(lectura_registres, list) is True, f"Classe Calendaritzador{error_lista}"

    def test_categories(self):
        lectura_registres = classificador.categories
        assert isinstance(lectura_registres, list) is True, f"Classe Classificador{error_lista}"

    def test_categories_registres(self):
        lectura_registres = classificador.categories_registrades
        assert isinstance(lectura_registres, list) is True, f"Classe Classificador{error_lista}"


if __name__ == '__main__':
    unittest.main()
