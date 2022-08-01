import datetime

import dateutil
from dateutil import parser
import pathlib
import sqlite3
import os
import sys
from sqlite3 import PARSE_DECLTYPES
from src.agents.formats import Registres_gui_comm, Registres_bbdd_comm, Registres_gui_nou, Registres_bbdd_nou, \
    Categoria_comm, Alumne_comm


class ModelDao:
    def __init__(self):
        super(ModelDao, self).__init__()
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"
        self.taula = ""
        self.conn = sqlite3.connect(self.ruta_bbdd)
        self.c = self.conn.cursor()


class AlumnesBbdd(ModelDao):
    def __init__(self, taula="alumnes"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

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
        parametre: str = "id,nom_alumne"
        self.cursor = self.conn.cursor()
        try:
            llista_alumnes = []
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            for i in consulta:
                persona = Alumne_comm(i[0], i[1])
                llista_alumnes.append(persona)
            self.cursor.close()
        except sqlite3.OperationalError as e:
            print(e)
            return False
        return llista_alumnes

    def llegir_alumne_individual(self, id_alumne: int):
        parametre: str = "id,nom_alumne"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM alumnes WHERE id = {id_alumne}"
            consulta = self.cursor.execute(ordre_consultar).fetchone()
            persona = Alumne_comm(consulta[0], consulta[1])
            self.cursor.close()
        except sqlite3.OperationalError as e:
            print(e)
            return False
        return persona

    def registrar_alumne(self, nom_alumne: str):
        self.cursor = self.conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (nom_alumne) VALUES ('{nom_alumne}')"
            self.cursor.execute(ordre_registrar)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def eliminar_alumne(self, missatge: list):
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

    def __init__(self, taula="registres"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de registres"""
        parametre: str = camp
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.close()
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
                missatge.append(Registres_bbdd_comm(registre[0], registre[1], registre[2], registre[3], registre[4]))
            return missatge
        except sqlite3.OperationalError:
            return False

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
                missatge.append(dades_individuals)
            return missatge
        except sqlite3.OperationalError:
            return False

    def crear_registre(self, input_creacio_registre: list):
        """Crea un nou registre"""
        if not isinstance(input_creacio_registre, list):
            return False
        else:
            for element in input_creacio_registre:
                if not isinstance(element, Registres_bbdd_nou):
                    return False
                else:
                    self.cursor = self.conn.cursor()
                    try:

                        ordre_registrar = f"INSERT INTO {self.taula} (id_alumne,id_categoria,data,descripcio) VALUES " + \
                                          f"({element.alumne},{element.categoria},'{element.data}','{element.descripcio}')"
                        self.cursor.execute(ordre_registrar)
                        self.conn.commit()
                        self.cursor.close()
                        return True
                    except sqlite3.OperationalError as e:
                        print(e)
                        return False

    def actualitzar_registre(self, missatge_actualitzar: list):
        """Actualitza un registre"""
        if not isinstance(missatge_actualitzar, list):
            raise TypeError("El missatge ha de ser una llista")
        else:
            for element in missatge_actualitzar:
                if not isinstance(element, Registres_bbdd_comm):
                    raise TypeError("El missatge ha de ser una llista amb el format correcte")
                else:
                    self.cursor = self.conn.cursor()
                    try:
                        ordre_actualitzar = f"UPDATE {self.taula} SET id_alumne = {element.alumne}, id_categoria = {element.categoria}, data = '{element.data}', descripcio = '{element.descripcio}' WHERE id = {element.id} "
                        self.cursor.execute(ordre_actualitzar)
                        self.conn.commit()
                        self.cursor.close()
                        return True
                    except sqlite3.OperationalError:
                        return False

    def eliminar_registre(self, missatge_eliminar: list):
        """Elimina un registre"""
        if not isinstance(missatge_eliminar, list):
            raise TypeError("El missatge ha de ser una llista")
        else:
            for element in missatge_eliminar:
                if not isinstance(element, Registres_bbdd_comm):
                    raise TypeError("El missatge ha de ser una llista amb el format correcte")
                else:
                    self.cursor = self.conn.cursor()
                    try:
                        ordre_eliminar = f"DELETE FROM {self.taula} WHERE id = {element.id}"
                        self.cursor.execute(ordre_eliminar)
                        self.conn.commit()
                        self.cursor.close()
                        return True
                    except sqlite3.OperationalError:
                        return False


class CategoriesBbdd(ModelDao):
    def __init__(self, taula="categories"):
        super().__init__()
        self.cursor = self.conn.cursor()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

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
                missatge.append(Categoria_comm(element[0], element[1]))
            return missatge
        except sqlite3.OperationalError:
            return False

    def crear_categoria(self, nom_categoria: str):
        """Crea una nova categoria"""
        self.cursor = self.conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (nom_categoria) VALUES ('{nom_categoria}')"
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

    def actualitzar_categoria(self, num_referencia: int, nom_categoria: str):
        """Actualitza una categoria"""
        self.cursor = self.conn.cursor()
        try:
            actualitzar = f"UPDATE {self.taula} SET nom_categoria = '{nom_categoria}' WHERE id = {num_referencia}"
            self.cursor.execute(actualitzar)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False


class DatesBbdd(ModelDao):
    def __init__(self, taula="dates"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de dates"""
        parametre: str = camp
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_dates(self):
        """Llegeix tota la taula de dates"""
        parametre: str = "id,data"
        self.cursor = self.conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = self.cursor.execute(ordre_consultar).fetchall()
            self.cursor.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def crear_data(self, data: int):
        """Crea una nova data"""
        self.cursor = self.conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (data) VALUES ('{data}')"
            self.cursor.execute(ordre_registrar)
            self.conn.commit()
            self.cursor.close()
            return True
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

    def actualitzar_data(self, num_referencia: int, data: str):
        """Actualitza una data"""
        self.cursor = self.conn.cursor()
        try:
            actualitzar = f"UPDATE {self.taula} SET data = '{data}' WHERE id = {num_referencia}"
            self.cursor.execute(actualitzar)
            self.conn.commit()
            self.cursor.close()
            return True
        except sqlite3.OperationalError:
            return False
