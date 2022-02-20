import sqlite3
import pandas as pd
import pandas.errors
import csv

arxiubbdd = "dades/registre.db"
alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"
l_alumnes_cons = []

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
        conn.execute('CREATE TABLE IF NOT EXISTS registres (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_alumne CHAR('
                     '50), categoria CHAR(20), data INTEGER DATE, descripcio CHAR(200))')
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        print("error")
        conn.close()


def demostracio_dades(nalumne, ncategoria, dregistre, trgistre):
    print(nalumne)
    print(ncategoria)
    print(dregistre)
    print(trgistre)


def registre_dades(nalumne, ncategoria, dregistre, tregistre):
    """Funció per a inserir el registre a la taula de la BBDD i, si no existeix, crear-la"""
    ordre_inserir_sql = 'INSERT INTO registres (nom_alumne, categoria, data, descripcio) VALUES (?, ?, ?, ?)'
    dades_a_registrar = (nalumne, ncategoria, dregistre, tregistre)
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()
        conn.execute(ordre_inserir_sql, dades_a_registrar)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        print("ERROR")


def consulta_alumnes():
    """Funció per a obtenir el llistat d'alumnes que tenen algun registre"""
    ordre_consulta_sql = 'SELECT DISTINCT nom_alumne FROM registres ORDER BY nom_alumne'
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()
        l_alumnes = conn.execute(ordre_consulta_sql)
        for row in l_alumnes:
            l_alumnes_cons.append(row[0])
        conn.close()
        print(l_alumnes_cons)
    except sqlite3.OperationalError:
        print("ERROR")


def consulta_dades():
    """Funció per a efectuar la consulta per nom d'alumne a la BBDD"""
    ordre_consulta_sql = 'SELECT FROM registres (nom_alumne, categoria, data, descripcio) VALUES (?, ?, ?, ?)'
    pass
