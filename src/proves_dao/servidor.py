from ModelDao import AlumnesBbdd, RegistresBbdd, CategoriesBbdd
from dateutil import parser
import sys
from datetime import date, timedelta, datetime


class Servidor:
    def __init__(self):
        self.info_categories = None
        self.info_registres = None
        self.info_alumnes = None
        self.alumnes = AlumnesBbdd()
        self.registres = RegistresBbdd()
        self.alumnes.llegir_taula()
        self.registres.llegir_taula()
        self.categories = CategoriesBbdd()
        self.categories.llegir_taula()
        self.registres = self.obtenir_registres()
        self.noms_alumnes = self.obtenir_noms()
        self.categories = self.obtenir_categories()

    def obtenir_registres(self):
        """Retorna una llista de registres convenients per a la presentació
        :list:
        """
        self.info_alumnes = self.alumnes.llegir_taula()
        self.info_registres = self.registres.llegir_taula()
        self.info_categories = self.categories.llegir_taula()
        # Condicio de seguretat per si no hi ha registres:
        if self.info_registres and self.info_alumnes and self.info_categories:
            registres_formatats = [list(registre) for registre in self.info_registres]
            # Substituim l'id de l'alumne de la llista de registres pel seu nom:
            for registre in registres_formatats:
                registre[1] = self.info_alumnes[registre[1] - 1][1]
            # Substituim l'id de la categoria de la llista de registres pel seu nom:
            for registre in registres_formatats:
                registre[2] = self.info_categories[registre[2] - 1][1]
            # Formatem la data:
            for registre in registres_formatats:
                registre[3] = parser.parse(registre[3]).strftime("%d/%m/%Y")
            return registres_formatats
        else:
            return False

    def obtenir_noms(self):
        """Retorna una llista de alumnes convenients per a la presentació :list:"""
        self.info_alumnes = self.alumnes.llegir_taula()
        # Condicio de seguretat per si no hi ha alumnes:
        if self.info_alumnes:
            noms = [alumne[1] for alumne in self.info_alumnes]
            self.noms_alumnes = [alumne[1] for alumne in self.info_alumnes]
            return noms
        else:
            return False

    def obtenir_categories(self):
        """Retorna una llista de categories convenients per a la presentació:list:"""
        self.info_categories = self.categories.llegir_taula()
        # Condicio de seguretat per si no hi ha categories:
        if self.info_categories:
            categories = [categoria[1] for categoria in self.info_categories]
            return categories
        else:
            return False


a = Servidor()
print(a.registres)
