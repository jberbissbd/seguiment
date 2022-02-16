import sqlite3
import pandas as pd
import pandas.errors
import csv

arxiubbdd = "dades/registre.db"
alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"


def lectura_dades():
    """Lectura dels arxius csv sobre alumnes i categories de seguiment"""
    global alumnat
    global categories

    try:
        with open(alumnat, "r") as file:
            dades_csv_al = pd.read_csv(file)
            al_seguiment = dades_csv_al["Alumnat"].values.tolist()
            file.close()
    except FileNotFoundError:
        alumnes = ["Alumnat"]
        print("Arxiu no trobat")
        with open(alumnat, "w") as file:
            writer = csv.writer(file)
            writer.writerow(alumnes)
    except pandas.errors.EmptyDataError:
        print("Sense dades d'alumnes, no es pot seguir")

    try:
        with open(categories) as file:
            dades_csv_cat = pd.read_csv(file)
            cat_seguiment: object = dades_csv_cat["Motius"].values.tolist()
            file.close()
    except FileNotFoundError:
        print("Llistat de categories buit, es torna a crear")
        motius_llista = ["Motius"]
        with open(categories, "w") as file:
            writer = csv.writer(file)
            writer.writerow(motius_llista)
    except pandas.errors.EmptyDataError:
        print("Sense categories, no es pot seguir")
    return al_seguiment, cat_seguiment


def bbdd_conn():
    global arxiubbdd
    conn = sqlite3.connect(arxiubbdd)
    try:
        conn.cursor()
        # conn.execute('CREATE TABLE registres (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_alumne TEXT, categoria TEXT, '
        # 'data INTEGER DATE, descripcio TEXT)')
        # conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        print("error")
        conn.close()


def registre_dades(nalumne, ncategoria, dregistre, tregistre):
    """Funció per a inserir el registre a la taula de la BBDD i, si no existeix, crear-la"""
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()

    except sqlite3.OperationalError:
        print("ERROR")


def consulta_dades():
    """Funció per a efectuar la consulta per nom d'alumne a la BBDD"""
    pass
