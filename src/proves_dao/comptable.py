from typing import List

from src.proves_dao.ModelDao import AlumnesBbdd, RegistresBbdd, CategoriesBbdd, DatesBbdd
from dateutil import parser
from src.agents.formats import Data, Registre_sortida, Alumne, Categoria, Registre_entrada
import sys
from datetime import date, timedelta, datetime
import sqlite3


class Comptable:
    def __init__(self):
        """Ordenar les taules de la base de dades perquè siguin més fàcils de llegir:"""
        self.info_categories = None
        self.info_registres = None
        self.info_alumnes = None
        self.alumnes = AlumnesBbdd()
        self.registradror = RegistresBbdd()
        self.alumnes.llegir_alumnes()
        self.registradror.lectura_registres()
        self.categories = CategoriesBbdd()
        self.categories.lectura_categories()
        self.registres = self.obtenir_registres()
        self.noms_alumnes = self.obtenir_noms()
        self.categories = self.obtenir_categories()

    def obtenir_registres(self):
        """Retorna una llista de registres convenients per a la presentació: list:
        """
        self.info_alumnes = self.alumnes.llegir_alumnes()
        self.info_registres = self.registradror.lectura_registres()
        self.info_categories = self.categories.lectura_categories()
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
                    Registre_sortida(registre[0], registre[1], registre[2], registre[3], registre[4]))
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
        self.info_categories = self.categories.lectura_categories()
        # Condicio de seguretat per si no hi ha categories:
        if self.info_categories:
            categories = [categoria[1] for categoria in self.info_categories]
            return categories
        else:
            return False

    def actualitzar_registre(self, registre_input):
        if not isinstance(registre_input, Registre_sortida):
            raise TypeError("El registre_input no és del tipus correcte.")
        else:
            # Convertim la data a un format que pugui ser llegit per la base de dades:
            registrenou = [registre_input.id, registre_input.alumne, registre_input.categoria, registre_input.data,
                           registre_input.descripcio]
            # Substituim el nom de la llista de registres pel seu id:
            for al in self.info_alumnes:
                if al[1] == registre_input.alumne:
                    registrenou[1] = al[0]
            # Substituim el nom de la llista de categories pel seu id:
            for cat in self.info_categories:
                if cat[1] == registre_input.categoria:
                    registrenou[2] = cat[0]
            # Canviem la data de format:
            registrenou[3] = registre_input.data
            if not isinstance(registrenou[1], int) or not isinstance(registrenou[2], int):
                return False
            else:
                self.registres.actualitzar_registre(registrenou[0], registrenou[1], registrenou[2], registrenou[3],
                                                    registrenou[4])
                return True

    def creacio_registres(self, registre_input):
        """Crea un registre a la base de dades:"""
        if not isinstance(registre_input, Registre_entrada):
            return False
        else:
            # Convertim la data a un format que pugui ser llegit per la base de dades:
            registrenou = [registre_input.alumne, registre_input.categoria, registre_input.data,
                           registre_input.descripcio]
            # Substituim el nom de la llista de registres pel seu id:
            for al in self.info_alumnes:
                if al[1] == registre_input.alumne:
                    registrenou[0] = al[0]
            # Substituim el nom de la llista de categories pel seu id:
            for cat in self.info_categories:
                if cat[1] == registre_input.categoria:
                    registrenou[1] = cat[0]
            # Canviem la data de format:
            registrenou[2] = date.isoformat(registre_input.data)
            if not isinstance(registrenou[0], int) or not isinstance(registrenou[1], int):
                return False
            print(registrenou[0], registrenou[1], registrenou[2], registrenou[3])
            self.registradror.crear_registre(registrenou[0], registrenou[1], registrenou[2], registrenou[3])
            return True


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
            llista_classes = []
            for r in self.info_dates:
                llista_dies = [list(r) for r in self.info_dates]

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
        self.alumnes = AlumnesBbdd()
        self.registres = RegistresBbdd()
        self.info_alumnes = self.alumnes.llegir_alumnes()
        self.info_alumnes_registrats = self.registres.lectura_alumnes_registrats()
        self.alumnat = self.obtenir_alumnes()
        self.alumnat_registres = self.obtenir_alumnes_registrats()

    def obtenir_alumnes(self):
        """Retorna una llista d'alumnes amb el format Alumne: list:"""
        # Condicio de seguretat per si no hi ha alumnes:
        alumnes_formatats = []
        if self.info_alumnes:
            noms = [alumne[1] for alumne in self.info_alumnes]
            for nom in noms:
                alumnes_formatats.append(Alumne(nom))
            return alumnes_formatats
        else:
            return False

    def obtenir_alumnes_registrats(self):
        """Retorna una llista d'alumnes amb el format Alumne: list:"""
        # Condicio de seguretat per si no hi ha alumnes:
        alumnes_registrats_formatats = []
        if self.info_alumnes and self.info_alumnes_registrats:
            alumnes_registrats = [list(alumne) for alumne in self.info_alumnes_registrats]
            noms = [list(alumne) for alumne in self.info_alumnes]
            for alumne in alumnes_registrats:
                for nom in noms:
                    if alumne[0] == nom[0]:
                        alumnes_registrats_formatats.append(Alumne(nom[1]))

            return alumnes_registrats_formatats
        else:
            return False

    def eliminar_alumnes(self, alumne):
        """Elimina un alumne de la base de dades"""
        id_comprovacio = self.obtenir_id_alumne(alumne)
        if id_comprovacio:
            self.alumnes.eliminar_alumne(id_comprovacio)
            return True
        else:
            return False

    def actualitzar_alumnes(self, alumne):
        """Actualitza un alumne de la base de dades"""
        id_comprovacio = self.obtenir_id_alumne(alumne)
        if id_comprovacio:
            self.alumnes.actualitzar_alumne(id_comprovacio, alumne.nom)
            return True
        else:
            return False

    def afegir_alumnes(self, alumne):
        """Afegix un alumne a la base de dades"""
        if isinstance(alumne, Alumne):
            self.alumnes.afegir_alumne(alumne.nom)
            return True
        else:
            return False

    def obtenir_id_alumne(self, alumne):
        """Retorna l'id d'un alumne"""
        if isinstance(alumne, Alumne):
            for alumne_bbdd in self.info_alumnes:
                if alumne_bbdd[1] == alumne.nom:
                    return alumne_bbdd[0]
        else:
            return False


class Classificador:
    def __init__(self):
        self.categories = CategoriesBbdd()
        self.info_categories = self.categories.lectura_categories()
        self.categories = self.obtenir_categories()

    def obtenir_categories(self):
        """Retorna una llista de categories amb el format Categoria: list:"""
        # Condicio de seguretat per si no hi ha categories:
        categories_formatades = []
        if self.info_categories:
            categories = [list(categoria) for categoria in self.info_categories]
            for categoria in categories:
                categories_formatades.append(Categoria(categoria[0], categoria[1]))
            return categories_formatades
        else:
            return False
