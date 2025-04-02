import os
from importlib.metadata import pass_none

import pytest

from src.seguiment.moduls.database import CreadorBBDD


@pytest.fixture(scope='class')
def ruta_prova():
    ruta = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(ruta)
    return ruta

class TestCreador:


    def test_ruta(self,ruta_prova):
        """Comprovacio de ruta per a la bbdd de test"""
        test_creador = CreadorBBDD()
        test_creador.bbdd_path = ruta_prova
        assert test_creador.bbdd_path == os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_ruta_arxiu_bbdd(self):
        """Comprovacio de ruta per a la bbdd real"""
        ruta_arxiu = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+'/src/seguiment/dades/'
        test_creador = CreadorBBDD()
        assert test_creador.bbdd_path == ruta_arxiu

    def test_creacio_arxiu(self, ruta_prova):
        """Comprovacio de la creacio de l'arxiu de base de dades"""
        test_creador = CreadorBBDD()
        test_creador.bbdd_path = ruta_prova
        test_creador.nom = '/test.db'
        test_creador.init_db()
        assert os.path.isfile(test_creador.bbdd_path+'/test.db')
        