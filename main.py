import sqlite3
import pandas as pd
from datetime import date
import pandas.errors
import csv
import sys

from PySide6.QtCore import QRect
from PySide6.QtWidgets import *

alumnat = 'dades/alumnat.csv'
categories = 'dades/categories.csv'
arxiubbdd = "dades/registre.db"

al_seguiment = ""
cat_seguiment = ""


# Definim funcions d'arrencada (llistes i bbdd):
def lectura_dades():
    global alumnat
    global categories
    global al_seguiment
    global cat_seguiment
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
            cat_seguiment = dades_csv_cat["Motius"].values.tolist()
            file.close()
    except FileNotFoundError:
        print("Llistat de categories buit, es torna a crear")
        motius_llista = ["Motius"]
        with open(categories, "w") as file:
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
        conn.close()

    except sqlite3.OperationalError:
        print("error")

    # conn.close()


def arrencada():
    lectura_dades()
    bbdd_conn()


class MainWin(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.resize(300, 200)
        arrencada()
        avui_real = date.today()
        avui_format = avui_real.strftime("%d/%m/%Y")
        # Configurem bloc d'alumnes:
        desplegable_al = QComboBox()
        desplegable_al.addItems(al_seguiment)
        alumnes_etiqueta = QLabel("Alumne: ")
        # Configurem bloc de motius:
        categories_etiqueta = QLabel("Motiu: ")
        desplegable_cat = QComboBox()
        desplegable_cat.addItems(cat_seguiment)
        # Afegim data
        data_etiqueta = QLabel("Data:")
        selector_data = QDateEdit(date=avui_real)
        selector_data.setDisplayFormat(u"dd/MM/yyyy")
        selector_data.setCalendarPopup(True)
        # Configurem disposició general
        conjunt = QFormLayout()
        conjunt.addRow(alumnes_etiqueta,desplegable_al)
        conjunt.addRow(categories_etiqueta, desplegable_cat)
        conjunt.addRow(data_etiqueta,selector_data)
        self.setLayout(conjunt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    programa = MainWin()
    programa.setWindowTitle("Seguiment d'alumnes")
    programa.show()
    sys.exit(app.exec())

# print(avui_format)
# print(al_seguiment)
# print(cat_seguiment)
