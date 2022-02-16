import sys
from datetime import date
from funcions import bbdd_conn, lectura_dades
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


def arrencada():
    global al_seguiment
    global cat_seguiment
    dades = lectura_dades()
    al_seguiment = dades[0]
    cat_seguiment = dades[1]
    bbdd_conn()


def traspas_alumnes(text):
    """Captura el nom de l'alumne seleccionat com a variable de python"""
    global al_registre
    al_registre = text
    print(al_registre)


def traspas_categoria(text):
    """Captura la categoria seleccionada com a variable de python"""
    global cat_registre
    cat_registre = text
    print(cat_registre)


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
        data_registre = selector_data.date()
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
