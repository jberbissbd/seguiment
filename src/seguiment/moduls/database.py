import pathlib
import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
# from .models import Student, TrackingEntry
# from .config_manager import get_term

def ruta_prova():
    ruta = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(ruta)
    return ruta


class CreadorBBDD:

    def __init__(self,nom='registre.db'):
        self.nom=nom
        self.bbdd_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/dades/'


    def init_db(self):
        ruta_dades = self.bbdd_path+self.nom
        if not os.path.isdir(self.bbdd_path):
            os.mkdir(self.bbdd_path)
        try:
            with sqlite3.connect(ruta_dades) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        student_group BLOB,
                        full_name BLOB
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        category_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        category_description BLOB
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        category_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        category_description BLOB
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                        data INTEGER NOT NULL,
                        descripcio BLOB,
                        id_alumne INTEGER NOT NULL,
                        id_categoria INTEGER NOT NULL,
                        FOREIGN KEY(id_categoria) REFERENCES "categories"("category_id") ON DELETE CASCADE,
                        FOREIGN KEY(id_alumne) REFERENCES "students"("student_id") ON DELETE CASCADE
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tracking_entries (
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        student_number INTEGER,
                        day TEXT NOT NULL,
                        category INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        trimestre TEXT NOT NULL,
                        FOREIGN KEY (student_number) REFERENCES students(student_id),
                        FOREIGN KEY (category) REFERENCES categories(category_id)
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(e)

        finally:
            cursor.close()

# [Totes les funcions de CRUD i consultes aquí...]