import sqlite3
import pandas as pd
from datetime import date
import pandas.errors
import csv

alumnat = '/dades/alumnat.csv'
categories = 'dades/categories.csv'

al_seguiment = ""
cat_seguiment = ""


def lectura_dades():
    global alumnat
    global al_seguiment
    global cat_seguiment
    try:
        with open(alumnat, "r") as file:
            al_seguiment = pd.read_csv(file)
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
        with open("categories.csv") as file:
            cat_seguiment = pd.read_csv(file)
            file.close()
    except FileNotFoundError:
        print("Llistat de categories buit, es torna a crear")
        motius_llista = ["Motius"]
        with open("categories.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(motius_llista)
    except pandas.errors.EmptyDataError:
        print("Sense categories, no es pot seguir")


def bbdd_conn():
    global arxiubbdd
    arxiubbdd = "dades/registre.db"
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()

    except sqlite3.OperationalError:
        print("error")

    # conn.close()


avui_real = date.today()
avui_format = avui_real.strftime("%d/%m/%Y")
bbdd_conn()
print(avui_format)
lectura_dades()
print(al_seguiment)
print(cat_seguiment)
