import pathlib
import sqlite3
import os
import sys


class ModelDao:
    def __init__(self):
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
        self.ruta_bbdd = None
        self.arxiu_bbdd = "registre.db"
        self.directory_base = os.path.dirname(self.arxiu_bbdd)
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula"""
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except Exception as e:
            print(e)
            return False

    def llegir_alumnes(self):
        parametre: str = "id,nom_alumne"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
        except sqlite3.OperationalError as e:
            print(e)
            return False
        return consulta

    def registrar_alumne(self, nom_alumne: str):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (nom_alumne) VALUES ('{nom_alumne}')"
            c.execute(ordre_registrar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def eliminar_alumne(self, id_alumne: int):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_eliminar = f"DELETE FROM {self.taula} WHERE id = {id_alumne}"
            c.execute(ordre_eliminar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def actualitzar_alumne(self, id_alumne: int, nom_alumne: str):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"UPDATE {self.taula} SET nom_alumne = '{nom_alumne}' WHERE id = {id_alumne}"
            c.execute(ordre_consultar)
            conn.commit()
            c.close()
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
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de registres"""
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_registres(self):
        """Llegeix tota la taula de registres"""
        parametre: str = "id,id_alumne,id_categoria,data,descripcio"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def crear_registre(self, id_alumne: int, id_categoria: int, data: int, descripcio: str):
        """Crea un nou registre"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (id_alumne,id_categoria,data,descripcio) VALUES " + \
                              f"({id_alumne},{id_categoria},{data},'{descripcio}') "
            c.execute(ordre_registrar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def actualitzar_registre(self, id_registre: int, id_alumne: int, id_categoria: int, data: int, descripcio: str):
        """Actualitza un registre"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"UPDATE {self.taula} SET id_alumne = {id_alumne}, id_categoria = {id_categoria}, " + \
                              f"data = {data}, descripcio = {descripcio} WHERE id = {id_registre}"
            c.execute(ordre_consultar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False


class CategoriesBbdd(ModelDao):
    def __init__(self, taula="categories"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de categories"""
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_categories(self):
        """Llegeix tota la taula de categories"""
        parametre: str = "id,categoria"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def crear_categoria(self, nom_categoria: str):
        """Crea una nova categoria"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (nom_categoria) VALUES ('{nom_categoria}')"
            c.execute(ordre_registrar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def eliminar_categoria(self, num_referencia):
        """Elimina una categoria"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            eliminar = f"DELETE FROM {self.taula} WHERE id = {num_referencia}"
            c.execute(eliminar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def actualitzar_categoria(self, num_referencia, nom_categoria):
        """Actualitza una categoria"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            actualitzar = f"UPDATE {self.taula} SET nom_categoria = '{nom_categoria}' WHERE id = {num_referencia}"
            c.execute(actualitzar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False


class DatesBbdd(ModelDao):
    def __init__(self, taula="dates"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        """Obtindre els registres d'un camp de la taula de dates"""
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def lectura_dates(self):
        """Llegeix tota la taula de dates"""
        parametre: str = "id,data"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            return consulta
        except sqlite3.OperationalError:
            return False

    def crear_data(self, data: int):
        """Crea una nova data"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_registrar = f"INSERT INTO {self.taula} (data) VALUES ({data})"
            c.execute(ordre_registrar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False

    def maxim_id_data(self):
        """Retorna l'id de la darrera data
        :int:
        """
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT MAX(id) FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
            consulta = consulta[0][0]
            return consulta
        except sqlite3.OperationalError:
            return False

    def actualitzar_data(self, num_referencia, data):
        """Actualitza una data"""
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            actualitzar = f"UPDATE {self.taula} SET data = {data} WHERE id = {num_referencia}"
            c.execute(actualitzar)
            conn.commit()
            c.close()
            return True
        except sqlite3.OperationalError:
            return False
