import csv
import sys
from datetime import date
from funcions import bbdd_conn as bbdd_conn
import pandas as pd
import pandas.errors
from PySide6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QGridLayout, QFormLayout, QDateEdit, \
    QApplication, QVBoxLayout, QTextEdit, QPushButton

# TODO: Registrar valors a la base de dades
# TODO: Afegir dades de trimestre
# TODO: Crear informe i exportar a Excel
# TODO: Moure funcions a arxiu funcions.


alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"

al_seguiment = ""
cat_seguiment = ""
al_registre: str = ""
cat_registre: str = ""
data_registre: str = ""


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


def arrencada():
    lectura_dades()
    bbdd_conn()


def traspas_alumnes(text):
    """Captura el nom de l'alumne seleccionat com a variable de python"""
    global al_registre
    al_registre = text


def traspas_categoria(text):
    """Captura la categoria seleccionada com a variable de python"""
    global cat_registre
    cat_registre = text


def traspas_data(text):
    """Captura la data seleccionada i la transforma a python"""
    global data_registre
    data_python = text.toPython()
    data_registre = data_python
    print(data_registre)


class MainWin(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(300, 200)
        arrencada()
        global al_registre
        global cat_registre
        global data_registre
        # Configurem bloc d'alumnes:
        desplegable_al = QComboBox()
        desplegable_al.addItems(al_seguiment)
        al_registre = desplegable_al.currentText()
        desplegable_al.currentTextChanged.connect(traspas_alumnes)
        alumnes_etiqueta = QLabel("Alumne: ")
        # Configurem bloc de motius:
        categories_etiqueta = QLabel("Motiu: ")
        desplegable_cat = QComboBox()
        desplegable_cat.addItems(cat_seguiment)
        cat_registre = desplegable_cat.currentText()
        desplegable_cat.currentTextChanged.connect(traspas_categoria)
        # Afegim data
        data_etiqueta = QLabel("Data:")
        selector_data = QDateEdit(date=date.today())
        selector_data.setDisplayFormat(u"dd/MM/yyyy")
        selector_data.setCalendarPopup(True)
        selector_data.dateChanged.connect(traspas_data)
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
        tbot.addWidget(qdesc_et, 0, 0)
        tbot.addWidget(qdesc, 0, 1)
        tbot.addLayout(bot_dist, 1, 0, 1, 2)
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
