import datetime
import sqlite3
from datetime import datetime
import dateutil.parser
import pandas as pd
import pandas.errors
import csv
import numpy as np
from dateutil.parser import *
import openpyxl

arxiubbdd = "dades/registre.db"
alumnat = "dades/alumnat.csv"
categories = "dades/categories.csv"
dates = "dades/dates.csv"
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
        with open(categories, "r") as file:
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

    try:
        with open(dates, "r") as file:
            dades_csv_trim = pd.read_csv(file)
            dates_trimestres = dades_csv_trim["Dates"].values.tolist()
            file.close()
            pass
    except pandas.errors.EmptyDataError:
        print("Error en les dates")
    return al_seguiment, cat_seguiment, dates_trimestres


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


def registre_dades(nom_alumne, nom_categoria, data_registre, text_registre):
    """Funció per a inserir el registre a la taula de la BBDD i, si no existeix, crear-la"""
    ordre_inserir_sql = 'INSERT INTO registres (nom_alumne, categoria, data, descripcio) VALUES (?, ?, ?, ?)'
    dades_a_registrar = (nom_alumne, nom_categoria, data_registre, text_registre)
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
    global l_alumnes_cons
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()
        l_alumnes_cons = []
        l_alumnes = conn.execute(ordre_consulta_sql)
        for row in l_alumnes:
            l_alumnes_cons.append(row[0])
        conn.close()
        return l_alumnes_cons
    except sqlite3.OperationalError:
        print("ERROR")


def consulta_dades(alumne):
    """Funció per a efectuar la consulta per nom d’alumne a la base de dades"""
    consulta = f"SELECT data, categoria,  descripcio FROM registres WHERE nom_alumne = \'{alumne}\' ORDER BY data"
    conn = sqlite3.connect(arxiubbdd)
    try:
        conn.cursor()
        resultat_consulta = conn.execute(consulta).fetchall()
        return resultat_consulta
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def exportar_xlsx(alumne):
    """Fa la consulta a l'arxiu sqlite a partir del nom de l'alumne, modifica el format i l'exporta a format Excel."""
    # Fem la connexió amb la base de dades:
    conn = sqlite3.connect(arxiubbdd)
    consulta = f"SELECT data, categoria,  descripcio FROM registres WHERE nom_alumne = \'{alumne}\' ORDER BY data"
    taula_pandas = pd.read_sql_query(consulta, conn, parse_dates='data')
    conn.close()

    def determinacio_trimestre(data_cons):
        """Assigna el trimestre segons la data del registre"""
        data_registre = data_cons['data']
        d1ertrim = datetime.strptime(lectura_dades()[2][0], '%Y-%m-%d')
        d2ontrim = datetime.strptime(lectura_dades()[2][1], '%Y-%m-%d')
        if data_registre <= d1ertrim:
            return 1
        elif data_registre < d2ontrim:
            return 2
        else:
            return 3

    # Apliquem la funció de determinació de trimestre:
    taula_pandas['Trimestre'] = taula_pandas.apply(lambda row: determinacio_trimestre(row), axis=1
                                                   , result_type='expand')
    # Classifiquem trimestre i categoria com a categories del pandas per a evitar problemes amb la repetició de valors
    taula_pandas['Trimestre'].astype('category')
    taula_pandas['categoria'].astype('category')
    # Definim com s'han d'agrupar les dades a la taula de sota:
    funcions_agregacio = {'descripcio': np.unique}
    # Executem la funció de lectura_dades per a obtenir les categories a tenir en compte a la taula, independentment
    # dels registres:
    noms_columnes = lectura_dades()[1]
    # Canviem l'orientació de la taula:
    taula_pivotada = pd.pivot_table(taula_pandas, index='Trimestre', columns='categoria', values='descripcio',
                                    fill_value="", aggfunc=funcions_agregacio, dropna=False) \
        .reindex(columns=noms_columnes)
    # Expandim els registres amb una llista com a valor (per exemple, dos registres el mateix dia)
    for columna_expandir in noms_columnes:
        taula_pivotada = taula_pivotada.explode(column=columna_expandir)
    print(taula_pivotada)
    taula_pivotada.to_excel(f'{alumne}.xlsx', merge_cells=True, startcol=1, startrow=1)
