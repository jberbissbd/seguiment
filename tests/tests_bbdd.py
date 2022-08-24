# -*- coding:utf-8 -*-
import os
import secrets
import sys
import unittest
from os.path import dirname

from faker import Faker

os.sys.path.append(dirname(dirname(__file__)))
os.sys.path.append(os.path.join(dirname(dirname(__file__))),"src")
from src.agents_bbdd import AlumnesBbdd, CategoriesBbdd, RegistresBbdd, DatesBbdd, AjudantDirectoris
from src.formats import Registres_bbdd_nou, RegistresBbddComm, AlumneNou, Alumne_comm, CategoriaComm, \
    DataGuiComm, DataNova

sys.path.append('./agents/formats')

fake = Faker("es_CA")
alumnes = AlumnesBbdd(taula="alumnes", modebbdd=2)
categories = CategoriesBbdd(taula="categories", modebbdd=2)
registres = RegistresBbdd(taula="registres", modebbdd=2)
calendari = DatesBbdd(taula="dates", modebbdd=2)
ruta_base_dades = AjudantDirectoris(2).base_dades

alumnes.ruta_bbdd = ruta_base_dades
registres.ruta_bbdd = ruta_base_dades
categories.ruta_bbdd = ruta_base_dades
calendari.ruta_bbdd = ruta_base_dades


class test_entrada_dades_bbdd(unittest.TestCase):
    def setUp(self, db=ruta_base_dades) -> None:
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_alumnes(self):
        nom_registrar = fake.name()
        missatge_registrar = [AlumneNou(nom_registrar)]
        resultat_registre = alumnes.registrar_alumne(missatge_registrar)
        assert resultat_registre is True, "Error al introduir nous valors a la taula d'alumnes"

    def test_alumnes_invers_general(self):
        nom_registrar: str = fake.name()
        missatge_registrar = AlumneNou(nom_registrar)
        self.assertRaises(TypeError, alumnes.registrar_alumne, missatge_registrar), "Agent alumnes admet valors " \
                                                                                    "invalids "

    def test_alumnes_invers_elements(self):
        nom_registrar: str = fake.name()
        missatge_registrar = AlumneNou(nom_registrar)
        self.assertRaises(TypeError, alumnes.registrar_alumne, missatge_registrar), "Els elements son invalids "

    def test_categories(self):
        categoria_registrar = fake.text()

        resultat_categories = categories.crear_categoria(categoria_registrar)
        assert resultat_categories is True, "Error al introduir nous valors a la taula de categories"

    def test_registres(self):
        id_alumne = secrets.choice(alumnes.test_llegir_alumnes())
        id_categoria = secrets.choice(categories.test_lectura_categories())
        data_registre = fake.date()
        descripcio_registre = fake.text()
        llista_registre = [Registres_bbdd_nou(id_alumne, id_categoria, data_registre, descripcio_registre)]
        resultat_crear_regitre = registres.crear_registre(llista_registre)
        assert resultat_crear_regitre is True, "Comprova si un registre amb el format Registre de missatgeria " \
                                               "s'introdueix "

    def test_dates(self):
        data_ficticia = fake.date()
        resultat_registre_data = calendari.crear_data([DataNova(data_ficticia)])
        assert resultat_registre_data is True, "Comprovacio al crear una data nova"


class test_actualitzacio(unittest.TestCase):
    """Classe per a comprovar operacio d'actualitzar"""

    def setUp(self) -> None:
        db = ruta_base_dades
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_alumnes(self):
        id_alumne = secrets.choice(alumnes.test_llegir_alumnes())
        nom_registrar = fake.name()
        missatge_registrar = [Alumne_comm(id_alumne, nom_registrar)]
        resultat_registre = alumnes.actualitzar_alumne(missatge_registrar)
        assert resultat_registre is True, "Error al introduir nous valors a la taula d'alumnes"

    def test_registres(self):
        id_registre = secrets.choice(registres.test_id_registre())
        id_alumne = secrets.choice(alumnes.test_llegir_alumnes())
        id_categoria = secrets.choice(categories.test_lectura_categories())
        data_registre = fake.date()
        descripcio_registre = fake.text()
        llista_actualitzar = [
            RegistresBbddComm(id_registre, id_alumne, id_categoria, data_registre, descripcio_registre)]
        resultat = registres.actualitzar_registre(llista_actualitzar)
        assert resultat is True, "Comprova si un registre amb el format Registre de missatgeria " \
                                 "s'introdueix "

    def test_categories(self):
        id_categoria = secrets.choice(categories.test_lectura_categories())
        categoria_registrar = fake.text()
        missatge_registrar = [CategoriaComm(id_categoria, categoria_registrar)]
        resultat_categories = categories.actualitzar_categoria(missatge_registrar)
        assert resultat_categories is True, "Error al introduir nous valors a la taula de categories"

    def test_dates(self):
        id_data = secrets.choice(calendari.test_dates())
        nova_data = fake.date()
        missatge_registrar = [DataGuiComm(id_data, nova_data)]
        resultat_registre = calendari.actualitzar_data(missatge_registrar)
        assert True is resultat_registre, "Error al introduir nous valors a la taula de dates"


class test_lectura(unittest.TestCase):

    def setUp(self) -> None:
        db = ruta_base_dades
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"
        self.resposta_llista = "Resultats han de ser una llista"

    def test_lectura_registres(self):
        llista_registres = registres.lectura_registres()
        assert isinstance(llista_registres, list), self.resposta_llista

    def test_lectura_alumnes(self):
        llista_registres = alumnes.llegir_alumnes()
        assert isinstance(llista_registres, list), self.resposta_llista

    def test_lectura_categories(self):
        llista_registres = categories.lectura_categories()
        assert isinstance(llista_registres, list), self.resposta_llista

    def test_format_individual_categories_variables(self):
        llista_registres = categories.lectura_categories()
        for element in llista_registres:
            nombre = element.id
            nom = element.nom
            assert isinstance(nombre, int), "Atribut id ha de ser un nombre"
            assert isinstance(nom, str), "Nom ha de ser un text"

    def test_lectura_dates(self):
        llista_registres = calendari.lectura_dates()
        assert isinstance(llista_registres, list), self.resposta_llista


class test_formats_resposta(unittest.TestCase):
    """Comprovacio que la resposta de la lectura de la base de dades segueixi els formats estblerts per
    cada taula.. """

    def setUp(self) -> None:
        db = ruta_base_dades
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_registres(self):
        llista_registres = registres.lectura_registres()
        for element in llista_registres:
            assert isinstance(element, RegistresBbddComm), "Registre no te el format RegistresBbddComm"

    def test_alumnes(self):
        llista_registres = alumnes.llegir_alumnes()
        for element in llista_registres:
            assert isinstance(element, Alumne_comm), "Alumne no te el format Alumne_comm"

    def test_categories(self):
        llista_registres = categories.lectura_categories()
        for element in llista_registres:
            assert isinstance(element, CategoriaComm), "Categoria no te el format CategoriaComm"

    def test_dates(self):
        llista_registres = calendari.lectura_dates()
        for element in llista_registres:
            assert isinstance(element, DataGuiComm), "Data no te el format DataGuiComm)"


class test_tipus_atributs(unittest.TestCase):
    """Test per a comprovar si tots els elements de la base de dades compleixen amb la missatgeria establerta"""

    def setUp(self) -> None:
        db = ruta_base_dades
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_registres(self):
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


class test_eliminacio(unittest.TestCase):
    def setUp(self) -> None:
        db = ruta_base_dades
        categories.ruta_bbdd = db
        registres.ruta_bbdd = db
        alumnes.ruta_bbdd = db
        calendari.ruta_bbdd = db
        categories.taula = "categories"
        registres.taula = "registres"
        alumnes.taula = "alumnes"
        calendari.taula = "dates"

    def test_registres(self):
        llista_registres = registres.lectura_registres()
        missatge_eliminar = [secrets.choice(llista_registres)]
        assert registres.eliminar_registre(missatge_eliminar) is True, "No s'ha pogut eliminar un element de la taula" \
                                                                       "registres"

    def test_alumnes(self):
        llista_alumnes = alumnes.llegir_alumnes()
        missatge_eliminar = [secrets.choice(llista_alumnes)]
        assert alumnes.eliminar_alumne(missatge_eliminar) is True, "No s'ha pogut eliminar un element de la taula " \
                                                                   "alumnes"

    def test_categories(self):
        llista_categories = categories.lectura_categories()
        missatge_eliminar = [secrets.choice(llista_categories)]
        assert alumnes.eliminar_alumne(missatge_eliminar) is True, "No s'ha pogut eliminar un element de la taula " \
                                                                   "alumnes"


def bbdd_lectura():
    bbdd_operacions_lectura = unittest.TestSuite()
    bbdd_operacions_lectura.addTest(test_lectura)
    bbdd_operacions_lectura.addTest(test_formats_resposta)
    bbdd_operacions_lectura.addTest(test_tipus_atributs)
    return bbdd_operacions_lectura


def bbdd_escriptura():
    escriptura = unittest.TestSuite()
    escriptura.addTest(test_entrada_dades_bbdd)
    return escriptura


def bbdd_actualitzacio():
    actualitzacio = unittest.TestSuite
    actualitzacio.addTest(test_actualitzacio)
    return actualitzacio


def bbdd_eliminacio():
    eliminacio = unittest.TestSuite()
    eliminacio.addTest(test_eliminacio)
    return eliminacio


if __name__ == "__main__":
    executor = unittest.TextTestRunner()
    executor.run(bbdd_lectura())
    executor.run(bbdd_escriptura())
    executor.run(bbdd_actualitzacio())
    executor.run(bbdd_eliminacio())
