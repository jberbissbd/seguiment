# -*- coding:utf-8 -*-
import os
import sys

sys.path.insert(0, "..")

import unittest
from dataclasses import is_dataclass
from os.path import dirname

from faker import Faker

os.sys.path.append(dirname(dirname(__file__)))
os.sys.path.append(os.path.join(dirname(dirname(__file__)), "src"))
from src.agents_gui import Calendaritzador, CapEstudis, Comptable, Classificador

fake = Faker("es_CA")
ERROR_LLISTA = ". Error: ha de proporcionar una llista."
ERROR_FORMAT = ". Error: La classe no respon amb els formats adequats."

registres = Comptable(modegui=2)
alumnes = CapEstudis(modegui=2)
calendari = Calendaritzador(modegui=2)
classificador = Classificador(modegui=2)


class TestLectura(unittest.TestCase):
    """Classe per a comprovar les operacions de lectura de dades"""

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        assert isinstance(lectura_registres, list) is True, f"Classe Comptable{ERROR_LLISTA}"

    def test_alumnes(self):
        lectura_registres = alumnes.alumnat
        assert isinstance(lectura_registres, list) is True, f"Classe Cap d'Estudis{ERROR_LLISTA}"

    def test_alumnes_registres(self):
        lectura_registres = alumnes.alumnat_registres
        assert isinstance(lectura_registres, list) is True, f"Classe Cap d'Estudis{ERROR_LLISTA}"

    def test_dates(self):
        lectura_registres = calendari.dates
        assert isinstance(lectura_registres, list) is True, f"Classe Calendaritzador{ERROR_LLISTA}"

    def test_categories(self):
        lectura_registres = classificador.categories
        assert isinstance(lectura_registres, list) is True, f"Classe Classificador{ERROR_LLISTA}"

    def test_categories_registres(self):
        lectura_registres = classificador.categories_registrades
        assert isinstance(lectura_registres, list) is True, f"Classe Classificador{ERROR_LLISTA}"


class TestFormatsLectura(unittest.TestCase):
    """Cas per a comprovar que compleix amb els formats establerts."""

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        for element in lectura_registres:
            assert is_dataclass(element) is True, f"Classe Comptable{ERROR_FORMAT}"

    def test_alumnes(self):
        lectura_registres = alumnes.alumnat
        for element in lectura_registres:
            assert is_dataclass(element) is True, f"Classe Cap d'Estudis{ERROR_FORMAT}"

    def test_alumnes_registres(self):
        lectura_registres = alumnes.alumnat_registres
        for element in lectura_registres:
            assert is_dataclass(element) is True, f"Classe Cap d'Estudis{ERROR_FORMAT}"


class TestTipusVariables(unittest.TestCase):

    def test_registres(self):
        lectura_registres = registres.obtenir_registres()
        for element in lectura_registres:
            numero = element.id
            data = element.data
            text = element.descripcio
            alumne_registre = element.alumne
            categoria_registre = element.categoria
            assert isinstance(numero, int), "ID del registre ha de ser un numero"
            assert is_dataclass(alumne_registre), "Alumne del registre ha de ser objecte Alumne_comm"
            assert is_dataclass(categoria_registre), "Categoria del registre ha de ser " \
                                                     "objecte CategoriaComm "
            assert isinstance(data, str), "Data del registre ha de ser text"
            assert isinstance(text, str), "Descripcio del registre ha de ser text"

    def test_alumnes(self):
        lectura_registres = alumnes.alumnat
        for element in lectura_registres:
            numero = element.id
            nomcomplet = element.nom
            assert isinstance(numero, int) is True, "ID del registre ha de ser un numero"
            assert isinstance(nomcomplet, str) is True, "Nom ha de ser un text"


if __name__ == '__main__':
    unittest.main()
