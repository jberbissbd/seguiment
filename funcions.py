import sqlite3

arxiubbdd = "dades/registre.db"


def bbdd_conn():
    global arxiubbdd
    arxiubbdd = "dades/registre.db"
    try:
        conn = sqlite3.connect(arxiubbdd)
        conn.cursor()
        conn.close()

    except sqlite3.OperationalError:
        print("error")
    conn.close()


def registre_dades():
    """Funció per a inserir el registre a la taula de la BBDD i, si no existeix, crear-la"""
    pass


def consulta_dades():
    """Funció per a efectuar la consulta per nom d'alumne a la BBDD"""
    pass
