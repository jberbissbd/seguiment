import csv
import datetime
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import pandas.errors

arxiubbdd = 'src/dades/registre.db'
alumnat = 'src/dades/alumnat.csv'
categories = 'src/dades/categories.csv'
dates = 'src/dades/dates.csv'
l_alumnes_cons = []


# TODO: Modificar alumnes i dates de trimestre per a funcionar amb BBDD enlloc de amb arxiu csv


class Lector:
    """Classe que llegeix les dades de la BBDD"""

    def __init__(self) -> object:
        self.arxiubbdd = 'src/dades/registre.db'

    @staticmethod
    def llista_alumnes():
        """Consulta els noms dels alumnes a la taula de noms"""
        ordre_consulta_sql = 'SELECT DISTINCT nom_alumne FROM alumnes ORDER BY nom_alumne'
        try:
            conn = sqlite3.connect(arxiubbdd)
            conn.cursor()
            r_alumnes = conn.execute(ordre_consulta_sql).fetchall()
            l_alumnes = [alumne for alumne in r_alumnes]
            return l_alumnes
        finally:
            conn.close()

    @staticmethod
    def llista_alumnes_desplegable():
        """Consulta els noms dels alumnes a la taula de noms"""
        ordre_consulta_sql = 'SELECT DISTINCT nom_alumne FROM alumnes ORDER BY nom_alumne'
        try:
            conn = sqlite3.connect(arxiubbdd)
            conn.cursor()
            r_alumnes = conn.execute(ordre_consulta_sql).fetchall()
            l_alumnes = [alumne[0] for alumne in r_alumnes]
            return l_alumnes
        finally:
            conn.close()

    @staticmethod
    def llista_alumnes_registres():
        """Funció per a obtenir el llistat d'alumnes que tenen algun registre"""
        ordre_consulta_sql = 'SELECT DISTINCT nom_alumne FROM registres ORDER BY nom_alumne'
        global l_alumnes_cons
        try:
            conn = sqlite3.connect(arxiubbdd)
            conn.cursor()
            l_alumnes_cons = []
            l_alumnes = conn.execute(ordre_consulta_sql)
            l_alumnes_cons = [alumne[0] for alumne in l_alumnes]
            conn.close()
            return l_alumnes_cons
        except sqlite3.OperationalError:
            print("ERROR")

    @staticmethod
    def llista_categories():
        """Consulta els noms de les categories a la taula de categories"""
        ordre_consulta_sql = 'SELECT DISTINCT categoria FROM categories ORDER BY categoria'
        try:
            conn = sqlite3.connect(arxiubbdd)
            conn.cursor()
            r_categories = conn.execute(ordre_consulta_sql).fetchall()
            l_categories = [categoria[0] for categoria in r_categories]
            return l_categories
        finally:
            conn.close()

    @staticmethod
    def llista_dates():
        """Consulta les dates de la taula de dates"""
        ordre_consulta_sql = 'SELECT DISTINCT data FROM dates ORDER BY data'
        try:
            conn = sqlite3.connect(arxiubbdd)
            conn.cursor()
            r_dates = conn.execute(ordre_consulta_sql).fetchall()
            l_dates = [date[0] for date in r_dates]
            return l_dates
        finally:
            conn.close()


def lectura_dades():
    """Lectura dels arxius csv sobre alumnes i categories de seguiment"""
    global alumnat
    global categories

    try:
        with open(alumnat, encoding='UTF8') as file:
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
        with open(categories, encoding='UTF8') as file:
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
        with open(dates, encoding='UTF8') as file:
            dades_csv_trim = pd.read_csv(file)
            dates_trimestres = dades_csv_trim["Dates"].values.tolist()
            file.close()

    except pandas.errors.EmptyDataError:
        print("Error en les dates")
    return al_seguiment, cat_seguiment, dates_trimestres


# TODO: refactoritzar per a substituir arxius csv per lectura BBDD

def bbdd_conn():
    global arxiubbdd
    conn = sqlite3.connect(arxiubbdd)

    try:
        conn.cursor()
        conn.execute('CREATE TABLE IF NOT EXISTS registres (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_alumne CHAR('
                     '50), categoria CHAR(20), data INTEGER DATE, descripcio BLOB)')
        conn.execute('CREATE TABLE IF NOT EXISTS alumnes (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_alumne BLOB)')
        conn.execute('CREATE TABLE IF NOT EXISTS dates (id INTEGER PRIMARY KEY AUTOINCREMENT, data INTEGER DATE)')
        conn.execute('CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria BLOB)')
        conn.commit()

    except sqlite3.OperationalError:
        print("error")
        conn.close()
    conn.cursor()
    comprovacio_motius = "SELECT * FROM categories"
    ecat = conn.execute(comprovacio_motius).fetchall()
    if len(ecat) == 0:
        try:
            insercio_categories = 'INSERT INTO categories (categoria) VALUES (?)'
            motius = ["Informació acadèmica", "Incidències", "Famílies (reunions)", "Escolta'm", "Observacions"]
            for motiu in motius:
                conn.execute(insercio_categories, (motiu,))
            conn.commit()
        except sqlite3.Error as e:
            print(e)
            conn.close()
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


def dates_lectura():
    consulta = 'SELECT ALL data FROM dates'
    conn = sqlite3.connect(arxiubbdd)
    try:
        conn.cursor()
        datestrim = conn.execute(consulta).fetchall()
        return datestrim
        # print(type(datestrim))
    finally:
        conn.close()


def dates_actualitzacio(data1, data2):
    ordre = 'UPDATE dates SET data=? WHERE id = ?'
    conn = sqlite3.connect(arxiubbdd)
    dates_posicio = [(data1, 1), (data2, 2)]
    try:
        conn.cursor()
        conn.executemany(ordre, dates_posicio)
        conn.commit()
    finally:
        conn.close()


def export_escoltam():
    conn = sqlite3.connect(arxiubbdd)
    noms_mesos = ['Setembre', 'Octubre', 'Novembre', 'Desembre', 'Gener', 'Febrer', 'Març', 'Abril', 'Maig', 'Juny']
    cat_filtre = "Escolta'm"
    consulta = f"SELECT data, categoria,  descripcio, nom_alumne FROM registres WHERE categoria = \"{cat_filtre}\" ORDER BY data"
    taula_escoltam = pd.read_sql_query(consulta, conn, parse_dates='data')
    conn.close()
    # Formategem deixant tan sols el mes, començant en majuscules:
    taula_escoltam['Mes'] = taula_escoltam.apply(lambda row: str(row['data'].strftime('%B')), axis=1,
                                                 result_type='expand')
    taula_escoltam['Mes'] = taula_escoltam.apply(lambda row: row['Mes'][3:len(row['Mes'])], axis=1,
                                                 result_type='expand')
    taula_escoltam['Mes'] = taula_escoltam.apply(lambda row: row['Mes'].capitalize(), axis=1, result_type='expand')
    taula_escoltam['Mes'].astype('category')
    funcions_agregacio = {'nom_alumne': np.unique}
    taula_escoltam_pivot = pd.pivot_table(taula_escoltam, index='Mes', values='nom_alumne', fill_value="",
                                          aggfunc=funcions_agregacio).reindex(index=noms_mesos)
    for columna_text in taula_escoltam_pivot:
        taula_escoltam_pivot = taula_escoltam_pivot.explode(column=columna_text)
    taula_escoltam_pivot.fillna(value="")
    print(taula_escoltam_pivot)


def export_global(alumne):
    """Fa la consulta a l'arxiu sqlite a partir del nom de l'alumne, modifica el format i l'exporta a format Excel."""
    # Fem la connexió amb la base de dades:
    conn = sqlite3.connect(arxiubbdd)
    consulta = f"SELECT data, categoria,  descripcio FROM registres WHERE nom_alumne = \'{alumne}\' ORDER BY data"
    taula_global = pd.read_sql_query(consulta, conn, parse_dates='data')
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
    taula_global['Trimestre'] = taula_global.apply(lambda row: determinacio_trimestre(row), axis=1
                                                   , result_type='expand')
    # Classifiquem trimestre i categoria com a categories del pandas per a evitar problemes amb la repetició de valors
    taula_global['Trimestre'].astype('category')
    taula_global['categoria'].astype('category')
    # Definim com s'han d'agrupar les dades a la taula de sota:
    funcions_agregacio = {'descripcio': np.unique}
    # Executem la funció de lectura_dades per a obtenir les categories a tenir en compte a la taula, independentment
    # dels registres:
    noms_columnes = lectura_dades()[1]
    # Canviem l'orientació de la taula:
    taula_pivotada = pd.pivot_table(taula_global, index='Trimestre', columns='categoria', values='descripcio',
                                    fill_value="", aggfunc=funcions_agregacio, dropna=False) \
        .reindex(columns=noms_columnes)
    # Expandim els registres amb una llista com a valor (per exemple, dos registres el mateix dia)
    for columna_expandir in noms_columnes:
        taula_pivotada = taula_pivotada.explode(column=columna_expandir)
    ruta_exportar = ".vscode/"
    nom_arxiu_exportar = f'{alumne}.xlsx'
    nom_complet = ruta_exportar + nom_arxiu_exportar
    taula_pivotada.to_excel(nom_complet, merge_cells=True, startcol=1, startrow=1)
