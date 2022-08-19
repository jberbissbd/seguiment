# -*- coding:utf-8 -*-
import os
import sqlite3
from os.path import dirname, abspath
import sys

# sys.path.append(os.path.abspath(dirname(__file__)))
sys.path.append(os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
import configparser
from src.agents.formats import RegistresBbddComm, Registres_bbdd_nou, CategoriaComm, Alumne_comm, \
    DataGuiComm, DataNova, AlumneNou

ERROR_LLISTA = "Error: el missatge ha de ser una llista."
ERROR_FORMAT = "Error: el missatge no té el format correcte."


def obtenir_ruta_config():
    """Proporciona la ruta dels arxius de configuracio"""
    localitzacio_config = os.path.normpath(
        os.path.join(os.path.abspath(dirname(dirname(abspath(__file__)))), "config.ini"))
    return localitzacio_config


def obtenir_ruta_icones():
    """Proporciona la ruta de la carpeta de les icones"""
    localitzacio_icones = os.path.normpath(
        os.path.join(os.path.abspath(dirname(dirname(abspath(__file__)))), "icones"))
    return localitzacio_icones


class AjudantDirectoris:
    """Proporciona la ruta d'acces absoluta a la localitzacio de la base de dades i de les icones."""

    def __init__(self, modebbdd: int):
        super().__init__()
        self.mode = modebbdd
        self.base_dades = self.establiment_mode()
        self.ruta_icones = obtenir_ruta_icones()

    def establiment_mode(self):
        """Estableix si funciona en mode de produccio o funcionament normal (1) o testing (2)"""
        directori_arrel = os.path.abspath(dirname(dirname(abspath(__file__))))
        ruta = None
        if self.mode == 1:
            localitzacio_bbdd = os.path.normpath(os.path.join(directori_arrel, "dades", "registre.db"))
            ruta = os.path.abspath(localitzacio_bbdd)
        elif self.mode == 2:
            localitzacio_bbdd = os.path.normpath(os.path.join(dirname(directori_arrel), "tests", "tests.db"))
            ruta = os.path.abspath(localitzacio_bbdd)
        return ruta


class ModelDao:
    """Patro per als DAO's subsequents"""

    def __init__(self, modebbdd: int):
        super().__init__()
        self.ruta_bbdd = AjudantDirectoris(modebbdd).base_dades
        self.taula = ""
        self.conn = sqlite3.connect(self.ruta_bbdd)
        self.cursor = self.conn.cursor()


class Liquidador(ModelDao):
    """Esborra les taules i la base de dades"""

    def __init__(self, model: int):
        super().__init__(modebbdd=model)

    def eliminar_basededades(self):
        """Eliminar l'arxiu de base de dades"""
        os.remove(self.ruta_bbdd)


def obtenir_valors_categories():
    """Metode per a parsejar les categories del config.ini"""
    config = configparser.ConfigParser()
    config.read(obtenir_ruta_config())
    valors = config.get('Categories', 'Defecte').split(', ')
    return valors


class Iniciador(ModelDao):
    """Comprova si existeixen les taules alumne, registres i dates"""

    def __init__(self, modebbdd: int):
        super().__init__(modebbdd)
        self.presencia_taula_alumne = self.comprova_existencia_taules("alumnes")
        self.presencia_taula_registres = self.comprova_existencia_taules("registres")
        self.presencia_taula_dates = self.comprova_existencia_taules("dates")
        self.presencia_taula_categories = self.comprova_existencia_taules("categories")
        self.valors_categories = obtenir_valors_categories()

    def comprova_existencia_taules(self, taula):
        """Comprova si la taula existeix a la base de dades o no"""
        self.taula = taula
        try:
            consulta = self.cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.taula}'").fetchone()
            if consulta[0] == self.taula:
                return True
            return False
        except sqlite3.OperationalError:
            return False

    def crea_taules(self):
        """Crea les taules necessaries per a la base de dades"""
        creacio_alumnes = False
        creacio_categories = False
        creacio_dates = False
        creacio_registres = False
        if self.presencia_taula_alumne is False:
            creacio_alumnes = AlumnesBbdd.crea_taula(self)
        if self.presencia_taula_categories is False:
            creacio_categories = CategoriesBbdd.crea_taula(self)
        if self.presencia_taula_dates is False:
            creacio_dates = DatesBbdd.crea_taula(self)
        if self.presencia_taula_registres is False:
            creacio_registres = RegistresBbdd.crea_taula(self)
        if creacio_alumnes and creacio_categories and creacio_dates and creacio_registres is True:
            return True
        return False


class AlumnesBbdd(ModelDao):
    """Realitza les operacions CRUD a la taula d'alumnes"""

    def __init__(self, modebbdd: int, taula="alumnes"):
        super().__init__(modebbdd)
        self.cursor = None
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

    def crea_taula(self):
        """Crea la taula si no existeix"""
        try:
            self.conn = sqlite3.connect(self.ruta_bbdd)
            self.cursor = self.conn.cursor()
            ordre_creacio = "CREATE TABLE IF NOT EXISTS alumnes (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_alumne BLOB)"
            self.cursor.execute(ordre_creacio)
            self.conn.commit()
            self.conn.close()
            return True
        except sqlite3.OperationalError:
            return False

    def destruir_taula(self):
        """Eliminar tots els registres de la taula"""
        self.cursor = self.conn.cursor()
        try:
            buidar_categories = f"DROP {self.taula}"
            self.cursor.execute(buidar_categories)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula"""
        parametre: str = camp
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def llegir_alumnes(self):
        """Llegeix les dades de la taula alumnes."""
        parametre: str = "id,nom_alumne"
        self.cursor = self.conn.cursor()
        try:
            llista_alumnes = []
            ordre_consultar = f"SELECT {parametre} FROM {self.taula} ORDER BY nom_alumne ASC"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            for i in consulta:
                persona = Alumne_comm(i[0], i[1])
                llista_alumnes.append(persona)
            self.cursor.close()
        except sqlite3.OperationalError:
            return False
        if len(llista_alumnes) > 0:
            return llista_alumnes
        return False

    def test_llegir_alumnes(self):
        """EXCLUSIU PER A TEST: OBTENIR EL REGISTRE MAXIM DE LA TAULA D'ALUMNES PER A FER TESTS"""
        parametre: str = "id"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            llista_ids = [item[0] for item in consulta]
            self.cursor.close()
        except sqlite3.OperationalError:
            return False
        if llista_ids:
            return llista_ids
        return False

    def llegir_alumne_individual(self, id_alumne: int):
        """Proporciona les dades d'un alumne amb el seu ID."""
        parametre: str = "id,nom_alumne"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM alumnes WHERE id = {id_alumne}"
            consulta = self.cursor.execute(ordre_consultar).fetchone()
            if consulta is not None:
                persona = Alumne_comm(consulta[0], consulta[1])
                self.cursor.close()
            else:
                return False
        except sqlite3.OperationalError:
            return False
        return persona

    def registrar_alumne(self, missatge_registrar: list):
        """Registra tots els alumnes de la llista de missatge registrar"""
        if not isinstance(missatge_registrar, list):
            raise TypeError("El missatge d'entrada ha de ser una llista")
        for element in missatge_registrar:
            if not isinstance(element, AlumneNou):
                raise TypeError("El format de cada element de l'entrada ha de ser AlumneNou")
            nom_alumne = element.nom
            self.cursor = self.conn.cursor()
            try:
                ordre_registrar = f"INSERT INTO {self.taula} (nom_alumne) VALUES ('{nom_alumne}')"
                self.cursor.execute(ordre_registrar)
                self.conn.commit()
                self.cursor.close()

            except sqlite3.OperationalError:
                return False
        return True

    def eliminar_alumne(self, missatge: list):
        """Elimina un alumne de la base de dades"""
        for element in missatge:
            id_alumne = element.id
            self.cursor = self.conn.cursor()
            try:
                ordre_eliminar = f"DELETE FROM {self.taula} WHERE id = {id_alumne}"
                self.cursor.execute(ordre_eliminar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False

    def actualitzar_alumne(self, missatge: list):
        """Actualitza un alumne de la base de dades"""
        for element in missatge:
            id_alumne = element.id
            nom_alumne = element.nom
            self.cursor = self.conn.cursor()
            try:
                ordre_consultar = f"UPDATE {self.taula} SET nom_alumne = '{nom_alumne}' WHERE id = {id_alumne}"
                self.cursor.execute(ordre_consultar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False


class RegistresBbdd(ModelDao):
    """Es relaciona amb la taula de registres"""

    def __init__(self, modebbdd, taula="registres"):
        super().__init__(modebbdd)
        self.cursor = None
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

    def crea_taula(self):
        """Crea la taula si no existeix"""
        try:
            self.conn = sqlite3.connect(self.ruta_bbdd)
            self.cursor = self.conn.cursor()
            ordre_creacio = """CREATE TABLE IF NOT EXISTS "registres" ("id" INTEGER NOT NULL PRIMARY KEY 
            AUTOINCREMENT UNIQUE, "data"
            INTEGER date, "descripcio" BLOB, "id_alumne" INTEGER NOT NULL, "id_categoria" INTEGER NOT
            NULL, FOREIGN KEY("id_categoria") REFERENCES "categories"("id") ON DELETE CASCADE, FOREIGN KEY(
            "id_alumne") REFERENCES "alumnes"("id") ON DELETE CASCADE )"""
            self.cursor.execute(ordre_creacio)
            self.conn.commit()
            self.conn.close()
            return True
        except sqlite3.OperationalError:
            return False

    def destruir_taula(self):
        """Eliminar tots els registres de la taula"""
        self.cursor = self.conn.cursor()
        try:
            buidar_registres = f"DROP {self.taula}"
            self.cursor.execute(buidar_registres)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def test_id_registre(self):
        """Obtindre la llista d'id's de la taula de registres"""
        parametre: str = "id"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            llista_ids = [item[0] for item in consulta]
            return llista_ids
        except sqlite3.OperationalError:
            return False

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de registres"""
        parametre: str = camp
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_registres(self):
        """Llegeix tota la taula de registres"""
        parametre: str = "id,id_alumne,id_categoria,data,descripcio"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula} ORDER BY data ASC"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            missatge = []
            for registre in consulta:
                missatge.append(RegistresBbddComm(registre[0], registre[1], registre[2], registre[3], registre[4]))
            return missatge
        except sqlite3.OperationalError:
            return False

    # noinspection PyTypeChecker
    def lectura_alumnes_registrats(self):
        """Llegeix els alumnes que tinguin algun registre"""
        parametre: str = "id_alumne"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT DISTINCT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            missatge = []
            for persona in consulta:
                dades_individuals = AlumnesBbdd.llegir_alumne_individual(self, persona[0])
                if dades_individuals:
                    missatge.append(dades_individuals)
            return missatge
        except sqlite3.OperationalError:
            return False

    def crear_registre(self, input_creacio_registre: list):
        """Crea un nou registre"""
        if not isinstance(input_creacio_registre, list):
            return False
        for element in input_creacio_registre:
            if not isinstance(element, Registres_bbdd_nou):
                return False
            self.cursor = self.conn.cursor()
            try:
                ordre_registrar = f"INSERT INTO {self.taula} (id_alumne,id_categoria,data,descripcio)" \
                                  f"VALUES ({element.alumne},{element.categoria},'{element.data}'," \
                                  f"'{element.descripcio}')"
                self.cursor.execute(ordre_registrar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False

    def actualitzar_registre(self, missatge_actualitzar: list):
        """Actualitza un registre"""
        if not isinstance(missatge_actualitzar, list):
            raise TypeError(ERROR_LLISTA)
        for element in missatge_actualitzar:
            if not isinstance(element, RegistresBbddComm):
                raise TypeError(ERROR_FORMAT)
            self.cursor = self.conn.cursor()
            try:
                ordre_actualitzar = f"UPDATE {self.taula} SET id_alumne = {element.alumne}," \
                                    f" id_categoria = {element.categoria}, data = '{element.data}'," \
                                    f" descripcio = '{element.descripcio}' WHERE id = {element.id} "
                self.cursor.execute(ordre_actualitzar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False

    def eliminar_registre(self, missatge_eliminar: list):
        """Elimina un registre"""
        if not isinstance(missatge_eliminar, list):
            raise TypeError(ERROR_LLISTA)
        for element in missatge_eliminar:
            if not isinstance(element, RegistresBbddComm):
                raise TypeError(ERROR_FORMAT)
            self.cursor = self.conn.cursor()
            try:
                ordre_eliminar = f"DELETE FROM {self.taula} WHERE id = {element.id}"
                self.cursor.execute(ordre_eliminar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False

    def eliminar_registre_alumne(self, missatge_eliminar: list):
        """Elimina un registre"""
        if not isinstance(missatge_eliminar, list):
            raise TypeError(ERROR_LLISTA)
        for element in missatge_eliminar:
            if not isinstance(element, Alumne_comm):
                raise TypeError("El missatge ha de ser una llista amb el format correcte")
            self.cursor = self.conn.cursor()
            try:
                ordre_eliminar = f"DELETE FROM {self.taula} WHERE id_alumne = {element.id}"
                self.cursor.execute(ordre_eliminar)
                self.conn.commit()
                self.cursor.close()
                return True
            except sqlite3.OperationalError:
                return False


class CategoriesBbdd(ModelDao):
    """Gestiona operacions CRUD de la taula de categories"""

    def __init__(self, modebbdd, taula="categories"):
        super().__init__(modebbdd)
        self.cursor = self.conn.cursor()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None
        self.valors_categories = obtenir_valors_categories()

    def crea_taula(self):
        """Crea la taula si no existeix"""
        self.conn = sqlite3.connect(self.ruta_bbdd)
        self.cursor = self.conn.cursor()
        try:

            ordre_creacio = "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                            "categoria BLOB)"
            self.cursor.execute(ordre_creacio)
            self.conn.commit()

        except sqlite3.OperationalError:
            return False
        if len(self.lectura_categories) == 0:
            try:
                insercio_categories = 'INSERT INTO categories (categoria) VALUES (?)'
                motius = self.valors_categories
                for motiu in motius:
                    self.cursor.execute(insercio_categories, (motiu,))
                    self.conn.commit()

            except sqlite3.OperationalError:
                return False
        self.conn.close()
        return True

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de categories"""
        parametre: str = camp
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_categories(self):
        """Llegeix tota la taula de categories"""
        parametre: str = "id,categoria"
        self.cursor = self.conn.cursor()
        try:
            missatge = []
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            for element in consulta:
                missatge.append(CategoriaComm(element[0], element[1]))
            return missatge
        except sqlite3.OperationalError:
            return False

    def test_lectura_categories(self):
        """EXCLUSIIU PER A TEST: OBTENIR EL REGISTRE MAXIM DE LA TAULA D'ALUMNES PER A FER TESTS"""
        parametre: str = "id"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            llista_ids = [item[0] for item in consulta]
            return llista_ids
        except sqlite3.OperationalError:
            return False

    def crear_categoria(self, nom_categoria: str):
        """Crea una nova categoria"""
        self.cursor = self.conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (categoria) VALUES ('{nom_categoria}')"
            self.cursor.execute(ordre_registrar)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def eliminar_categoria(self, num_referencia: int):
        """Elimina una categoria"""
        self.cursor = self.conn.cursor()
        try:
            eliminar = f"DELETE FROM {self.taula} WHERE id = {num_referencia}"
            self.cursor.execute(eliminar)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def actualitzar_categoria(self, missatge: list):
        """Actualitza una categoria
        :param missatge: Llista amb instancies de CategoriaComm.
        :arg missatge formada per instancies de CategoriaComm.
        :returns Fals si no es pot realitzar l'operacio.
        :raises TypeError si els formats d'enttrada no son correctes.
        """
        self.cursor = self.conn.cursor()
        if not isinstance(missatge, list):
            raise TypeError("Les dades han de tenir format de llista")
        for item in missatge:
            if not isinstance(item, CategoriaComm):
                raise TypeError("Les dades han de seguir el format CategoriaComm")
            try:
                num_referencia = item.id
                nom_categoria = item.nom
                actualitzar = f"UPDATE {self.taula} SET categoria = '{nom_categoria}'" \
                              f"WHERE id = {num_referencia}"
                self.cursor.execute(actualitzar)
                self.conn.commit()
                self.cursor.close()
            except sqlite3.OperationalError:
                return False
        return True

    def destruir_taula(self):
        """Eliminar tots els registres de la taula"""
        self.cursor = self.conn.cursor()
        try:
            buidar_categories = f"DROP {self.taula}"
            self.cursor.execute(buidar_categories)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False


class DatesBbdd(ModelDao):
    """Gestiona operacions CRUD de la taula de dates"""

    def __init__(self, modebbdd, taula="dates"):
        super().__init__(modebbdd)
        self.cursor = None
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

    def crea_taula(self):
        """Crea la taula si no existeix"""
        try:
            self.conn = sqlite3.connect(self.ruta_bbdd)
            self.cursor = self.conn.cursor()
            ordre_creacio = "CREATE TABLE IF NOT EXISTS dates (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)"
            self.cursor.execute(ordre_creacio)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            return False
        finally:
            self.conn.close()

    def lectura_dates(self):
        """Llegeix tota la taula de dates"""
        parametre: str = "id,data"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            if consulta is not None:
                missatge_lectura_dates = [DataGuiComm(element[0], element[1]) for element in consulta]
                return missatge_lectura_dates
            return False
        except sqlite3.OperationalError:
            return False

    def crear_data(self, llista_dates: list):
        """Crea una nova data"""
        self.cursor = self.conn.cursor()
        if not isinstance(llista_dates, list):
            raise TypeError("L'entrada de dates ha de ser una llista")
        for item in llista_dates:
            if not isinstance(item, DataNova):
                raise TypeError("La nova data ha de la classe DataNova")
            try:
                ordre_registrar = f"INSERT INTO {self.taula} (data) VALUES ('{item.dia}')"
                self.cursor.execute(ordre_registrar)
                self.conn.commit()
                self.cursor.close()
            except sqlite3.OperationalError:
                return False
                # Retorna fals si el registre no te el format adequat
        return True
        # Retorna Fals si els elements d'entrada no son una llista.

    def test_dates(self):
        """EXCLUSIIU PER A TEST: OBTENIR EL REGISTRE MAXIM DE LA TAULA DE DATES PER A FER TESTS"""
        parametre: str = "id"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            llista_ids = [item[0] for item in consulta]
            return llista_ids
        except sqlite3.OperationalError:
            return False

    def maxim_id_data(self):
        """Retorna l'id de la darrera data
        :int:
        """
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT MAX(id) FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.conn.close()
            consulta = consulta[0][0]
            return consulta
        except sqlite3.OperationalError:
            return False

    def actualitzar_data(self, missatge_actualizacio: list):
        """Actualitza una data"""
        if not isinstance(missatge_actualizacio, list):
            raise TypeError("El parametre d'entrada ha de ser una llista")
        for element in missatge_actualizacio:
            if not isinstance(element, DataGuiComm):
                raise TypeError("Els elements per actualitzar han de ser de la categoria DataGuiComm")
            self.cursor = self.conn.cursor()
            try:
                data = element.dia
                num_referencia = element.id
                actualitzar = f"UPDATE {self.taula} SET data = '{data}' WHERE id = {num_referencia}"
                self.cursor.execute(actualitzar)
                self.conn.commit()
                self.cursor.close()
            except sqlite3.OperationalError:
                return False
        return True

    def destruir_taula(self):
        """Eliminar tots els registres de la taula"""
        self.cursor = self.conn.cursor()
        try:
            buidar_categories = f"DROP FROM {self.taula}"
            self.cursor.execute(buidar_categories)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False
