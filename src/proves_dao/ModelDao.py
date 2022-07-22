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

    def llegir_taula(self):
        parametre: str = "id,nom_alumne"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        try:
            ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
            consulta = c.execute(ordre_consultar).fetchall()
            c.close()
        except Exception as e:
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
        except Exception as e:

            print(e)
            return False

    def eliminar_alumne(self, id_alumne: int):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        eliminar = f"DELETE FROM {self.taula} WHERE id = {id_alumne}"
        c.execute(eliminar)
        conn.commit()
        c.close()
        return True

    def actualitzar_alumne(self, id_alumne: int, nom_alumne: str):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_consultar = f"UPDATE {self.taula} SET nom_alumne = '{nom_alumne}' WHERE id = {id_alumne}"
        c.execute(ordre_consultar)
        conn.commit()
        c.close()
        return True


class RegistresBbdd(ModelDao):
    def __init__(self, taula="registres"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
        consulta = c.execute(ordre_consultar).fetchall()
        c.close()
        return consulta

    def llegir_taula(self):
        parametre: str = "id,id_alumne,id_categoria,data,descripcio"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
        consulta = c.execute(ordre_consultar).fetchall()
        c.close()
        return consulta

    def registrar(self, id_alumne: int, id_categoria: int, data: int, descripcio: str):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_registrar = f"INSERT INTO {self.taula} (id_alumne,id_categoria,data,descripcio) VALUES ({id_alumne},{id_categoria},{data},'{descripcio}') "
        c.execute(ordre_registrar)
        conn.commit()
        c.close()
        return True


class CategoriesBbdd(ModelDao):
    def __init__(self, taula="categories"):
        super().__init__()
        self.taula = taula
        self.ordre_consultar = None
        self.parametre = None
        self.ruta_bbdd = "/home/jordi/Documents/Projectes/seguiment/src/dades/registre.db"

    def consultar_camp(self, camp: str):
        parametre: str = camp
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
        consulta = c.execute(ordre_consultar).fetchall()
        c.close()
        return consulta

    def llegir_taula(self):
        parametre: str = "id,categoria"
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_consultar = f"SELECT {parametre} FROM {self.taula}"
        consulta = c.execute(ordre_consultar).fetchall()
        c.close()
        return consulta

    def registrar(self, nom_categoria: str):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        ordre_registrar = f"INSERT INTO {self.taula} (nom_categoria) VALUES ('{nom_categoria}')"
        c.execute(ordre_registrar)
        conn.commit()
        c.close()
        return True

    def eliminar(self, num_referencia):
        conn = sqlite3.connect(self.ruta_bbdd)
        c = conn.cursor()
        eliminar = f"DELETE FROM {self.taula} WHERE id = {num_referencia}"
        c.execute(eliminar)
        conn.commit()
        c.close()
        return True
