from ModelDao import AlumnesBbdd, RegistresBbdd, CategoriesBbdd, DatesBbdd
from dateutil import parser
from src.agents.formats import Data, Registre, Alumne, Categoria
import sys
from datetime import date, timedelta, datetime
from dataclasses import dataclass, field, fields


class Comptable:
    def __init__(self):
        """Ordenar les taules de la base de dades perquè siguin més fàcils de llegir:"""
        self.info_categories = None
        self.info_registres = None
        self.info_alumnes = None
        self.alumnes = AlumnesBbdd()
        self.registres = RegistresBbdd()
        self.alumnes.llegir_alumnes()
        self.registres.lectura_registres()
        self.categories = CategoriesBbdd()
        self.categories.lectura_categories()
        self.registres = self.obtenir_registres()
        self.noms_alumnes = self.obtenir_noms()
        self.categories = self.obtenir_categories()

    def obtenir_registres(self):
        """Retorna una llista de registres convenients per a la presentació: list:
        """
        self.info_alumnes = self.alumnes.llegir_alumnes()
        self.info_registres = self.registres.llegir_taula()
        self.info_categories = self.categories.llegir_taula()
        # Condicio de seguretat per si no hi ha registres:
        if self.info_registres and self.info_alumnes and self.info_categories:
            registres_formatats = [list(registre) for registre in self.info_registres]
            # Substituim l'id de l'alumne de la llista de registres pel seu nom:
            registres_classes = []
            for registre in registres_formatats:
                # Obtenim el nom de l'alumne:
                registre[1] = self.info_alumnes[registre[1] - 1][1]
                # Substituim l'id de la categoria de la llista de registres pel seu nom:
                registre[2] = self.info_categories[registre[2] - 1][1]
                # Formatem la data:
                registre[3] = parser.parse(registre[3]).strftime("%d/%m/%Y")
                registres_classes.append(
                    Registre(registre[0], registre[1], registre[2], registre[3], registre[4]))
            return registres_classes
        else:
            return False

    def obtenir_noms(self):
        """Retorna una llista d'alumnes convenients per a la presentació: list:"""
        self.info_alumnes = self.alumnes.llegir_alumnes()
        # Condicio de seguretat per si no hi ha alumnes:
        if self.info_alumnes:
            noms = [alumne[1] for alumne in self.info_alumnes]
            self.noms_alumnes = [alumne[1] for alumne in self.info_alumnes]
            return noms
        else:
            return False

    def obtenir_categories(self):
        """Retorna una llista de categories convenients per a la presentació: list:"""
        self.info_categories = self.categories.llegir_alumnes()
        # Condicio de seguretat per si no hi ha categories:
        if self.info_categories:
            categories = [categoria[1] for categoria in self.info_categories]
            return categories
        else:
            return False
#TODO: Afegir mecanisme per a actualitzar els registres de la base de dades.


class Calendaritzador:

    def __init__(self):
        self.datador = DatesBbdd()
        self.info_dates = self.datador.lectura_dates()
        self.dates = self.conversio_dates()
        self.maxim_id = self.datador.maxim_id_data()

    def conversio_dates(self):
        """Obte els registres de dates, els transforma a llista i converteix dates a format dia/mes/any, basades en
        classe Data """
        if self.datador.lectura_dates():
            self.info_dates = self.datador.lectura_dates()
            for r in self.info_dates:
                llista_dies = [list(r) for r in self.info_dates]
                llista_classes = []
                for dia in llista_dies:
                    dia[1] = parser.parse(dia[1]).strftime("%d/%m/%Y")
                    llista_classes.append(Data(dia[0], dia[1]))
            return llista_classes
        else:
            return False

    def actualitza_dates(self, aniversari):
        """Actualitza la base de dades amb la data subministrada, comprovant si es una data nova o no
        :type aniversari: Data
        """
        if isinstance(aniversari, Data):
            num_data = [dia.id for dia in self.dates]
            if aniversari.id not in num_data:
                return False
            else:
                # Convertim la data a tipus string per a la base de dades:
                dia_python = parser.parse(aniversari.dia).strftime("%Y-%m-%d")
                self.datador.actualitza_dates(aniversari.id, dia_python)
                return True
        else:
            return False


class CapEstudis:
    def __init__(self):
        self.comptable = Comptable()
        self.calendaritzador = Calendaritzador()

    def mostrar_registres(self):
        """Mostra els registres de la base de dades"""
        if self.comptable.registres:
            for registre in self.comptable.registres:
                print(registre)
        else:
            print("No hi ha registres")

    def mostrar_alumnes(self):
        """Mostra els alumnes de la base de dades"""
        if self.comptable.noms_alumnes:
            for alumne in self.comptable.noms_alumnes:
                print(alumne)
        else:
            print("No hi ha alumnes")

    def mostrar_categories(self):
        """Mostra les categories de la base de dades"""
        if self.comptable.categories:
            for categoria in self.comptable.categories:
                print(categoria)
        else:
            print("No hi ha categories")

    def mostrar_dates(self):
        """Mostra les dates de la base de dades"""
        if self.calendaritzador.dates:
            for dia in self.calendaritzador.dates:
                print(dia)
        else:
            print("No hi ha dates")

    def afegir_registre(self, alumne, categoria, data, descripcio):
        """Afegix un registre a la base de dades"""
        if isinstance(alumne, str) and isinstance(categoria, str) and isinstance(data, str) and isinstance(
                descripcio, str):
            alumne_id = self.comptable.alumnes.obtenir_id_alumne(alumne)
            categoria_id = self.comptable.categories.obtenir_id_categoria(categoria)
            data_id = self.calendaritzador


a = Calendaritzador()
b = Registre(1, 3, 2, "01/01/2020", "Descripció")
print(fields(b))
