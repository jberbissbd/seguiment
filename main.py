import sqlite3
import pandas as pd
from datetime import date
import pandas.errors
import csv
import sys

from PySide6 import QtGui
from PySide6.QtWidgets import *

# TODO: Consultar https://realpython.com/python-pyqt-layout/


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
        # TODO: Arreglar càrrega de fitxer
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
        # Configurem disposició:
        disp_general = QVBoxLayout()

        # Configurem part formulari:
        form_dist = QFormLayout()
        form_dist.addRow(alumnes_etiqueta, desplegable_al)
        form_dist.addRow(categories_etiqueta, desplegable_cat)
        form_dist.addRow(data_etiqueta, selector_data)

        # Configurem text i botons:
        tbot = QGridLayout()
        qdesc_et = QLabel("Descripció:")
        qdesc = QTextEdit()
        regbot = QPushButton("Registrar")
        expbot = QPushButton("Exportar informe")
        bot_dist = QHBoxLayout()
        bot_dist.addWidget(regbot)
        bot_dist.addWidget(expbot)
        tbot.addWidget(qdesc_et,0,0)
        tbot.addWidget(qdesc,0,1)
        tbot.addLayout(bot_dist,1,0,1,2)
        # Configuració final de la part general:
        disp_general.addLayout(form_dist)
        disp_general.addLayout(tbot)

        self.setLayout(disp_general)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    programa = MainWin()
    programa.setWindowTitle("Seguiment d'alumnes")
    programa.show()
    sys.exit(app.exec())

# print(avui_format)
# print(al_seguiment)
# print(cat_seguiment)
