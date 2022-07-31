import itertools

import dateutil

from src.agents.agents_bbdd import AlumnesBbdd, RegistresBbdd, CategoriesBbdd, DatesBbdd
from dateutil import parser

from src.agents.formats import Data_gui_comm, Registres_gui_comm, Alumne_comm, Registres_gui_nou, \
    Registres_bbdd_nou


class Comptable:
    def __init__(self):
        """Ordenar les taules de la base de dades perquè siguin més fàcils de llegir:"""
        self.info_categories = None
        self.info_registres = None
        self.info_alumnes = None
        self.alumnes = AlumnesBbdd()
        self.registrador = RegistresBbdd()
        self.alumnes.llegir_alumnes()
        self.registrador.lectura_registres()
        self.categories = CategoriesBbdd()
        self.categories.lectura_categories()
        self.registres = self.obtenir_registres()
        self.noms_alumnes = self.obtenir_noms()
        self.categories = self.obtenir_categories()

    def obtenir_registres(self):
        """Retorna una llista de registres convenients per a la presentació: list:
        """
        self.info_alumnes = self.alumnes.llegir_alumnes()
        self.info_registres = self.registrador.lectura_registres()
        self.info_categories = self.categories.lectura_categories()
        # Condicio de seguretat per si no hi ha registres:
        if self.info_registres and self.info_alumnes and self.info_categories:
            registres_entrada = self.info_registres
            missatge_registres = []
            # Substituim l'id de l'alumne de la llista de registres pel seu nom:

            for registre in registres_entrada:
                registre_proces = []
                registre_proces.append(registre.id)
                # Obtenim el nom de l'alumne:
                for alumne in self.info_alumnes:
                    if alumne.id == registre.alumne:
                        registre_proces.append(alumne)
                # Substituim l'id de la categoria de la llista de registres pel seu nom:
                for categoria in self.info_categories:
                    if categoria.id == registre.categoria:
                        registre_proces.append(categoria)
                registre_proces.append(registre.data)
                registre_proces.append(registre.descripcio)
                registre_tractat = Registres_gui_comm(registre_proces[0], registre_proces[1], registre_proces[2],registre_proces[3], registre_proces[4])
                missatge_registres.append(registre_tractat)

            return missatge_registres
        else:
            return False

    def obtenir_noms(self):
        """Retorna una llista d'alumnes convenients per a la presentació: list:"""
        self.info_alumnes = self.alumnes.llegir_alumnes()
        # Condicio de seguretat per si no hi ha alumnes:
        if self.info_alumnes:
            noms = [alumne.nom for alumne in self.info_alumnes]
            return noms
        else:
            return False

    def obtenir_categories(self):
        """Retorna una llista de categories convenients per a la presentació: list:"""
        self.info_categories = self.categories.lectura_categories()
        # Condicio de seguretat per si no hi ha categories:
        if self.info_categories:
            categories = [categoria.nom for categoria in self.info_categories]
            return categories
        else:
            return False

    def actualitzar_registre(self, registre_input):
        if not isinstance(registre_input, Registres_gui_comm):
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

    def crear_registre(self, registre_input):
        """Crea un registre a la base de dades:"""
        if not isinstance(registre_input, list):
            return False
        else:
            missatge_registre_bbddd = []
            # Processem els registres nous:
            for info in registre_input:
                if not isinstance(info, Registres_gui_nou):
                    return False
                else:
                    # Convertim la data a un format que pugui ser llegit per la base de dades:
                    registrenou = Registres_bbdd_nou(info.alumne.id, info.categoria.id, info.data, info.descripcio)
                    if not isinstance(registrenou.alumne, int) or not isinstance(registrenou.categoria, int):
                        return False

                    missatge_registre_bbddd.append(registrenou)
                self.registrador.crear_registre(missatge_registre_bbddd)
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
                    dia[1] = dateutil.parser.parse(dia[1]).strftime("%d/%m/%Y")
                    llista_classes.append(Data_gui_comm(dia[0], dia[1]))
            return llista_classes
        else:
            return False

    def actualitza_dates(self, aniversari):
        """Actualitza la base de dades amb la data subministrada, comprovant si es una data nova o no
        :type aniversari: Data_gui_comm
        """
        if isinstance(aniversari, Data_gui_comm):
            num_data = [dia.id for dia in self.dates]
            if aniversari.id not in num_data:
                return False
            else:
                # Convertim la data a tipus string per a la base de dades:
                dia_python = dateutil.parser.parse(aniversari.dia).strftime("%Y-%m-%d")
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
            for alumne in self.info_alumnes:
                alumnes_formatats.append(Alumne_comm(alumne.id, alumne.nom))
            return alumnes_formatats
        else:
            return False

    def obtenir_alumnes_registrats(self):
        """Retorna una llista d'alumnes amb el format Alumne: list:"""
        # Condicio de seguretat per si no hi ha alumnes:
        alumnes_registrats_formatats = []

        if self.info_alumnes and self.info_alumnes_registrats:
            alumnes_registrats = list(itertools.chain(*self.info_alumnes_registrats))
            alumnes_registrats_formatats = []
            persones = self.info_alumnes
            for alumne in alumnes_registrats:
                for persona in persones:
                    if alumne == persona.id:
                        alumnes_registrats_formatats.append(Alumne_comm(persona.id, persona.nom))

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
        """Afegeix un alumne a la base de dades"""
        if isinstance(alumne, Alumne_comm):
            self.alumnes.afegir_alumne(alumne.nom)
            return True
        else:
            return False

    def obtenir_id_alumne(self, alumne):
        """Retorna l'id d'un alumne"""
        if isinstance(alumne, Alumne_comm):
            for alumne_bbdd in self.info_alumnes:
                if alumne_bbdd[1] == alumne.nom:
                    return alumne_bbdd[0]
        else:
            return False


class Classificador:
    def __init__(self):
        self.categories = CategoriesBbdd()
        self.info_categories = self.categories.lectura_categories()
        self.categories = self.info_categories
