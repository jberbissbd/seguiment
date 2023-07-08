from dataclasses import dataclass


@dataclass(repr=False)
class Registresguicomm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a registres ja existents"""
    id: int
    alumne: dataclass
    categoria: dataclass
    data: str
    descripcio: str


@dataclass(repr=False)
class RegistresBbddComm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a registres ja existents"""
    id: int
    alumne: int
    categoria: int
    data: str
    descripcio: str


@dataclass(repr=False)
class Registres_gui_nou:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a registres no existents"""
    alumne: dataclass
    categoria: dataclass
    data: str
    descripcio: str


@dataclass(repr=False)
class Registres_bbdd_nou:
    """Classe per a la missatgeria entre els agents i la base de dades, per a registres no existents"""
    alumne: int
    categoria: int
    data: str
    descripcio: str


@dataclass(repr=False)
class Alumne_comm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a alumnes ja existents"""
    id: int
    nom: str


@dataclass(repr=False)
class AlumneNou:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a alumnes nous"""
    nom: str


@dataclass(repr=False)
class CategoriaComm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a categories ja existents"""
    id: int
    nom: str


@dataclass(repr=False)
class CategoriaNova:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a categories ja existents"""
    nom: str


@dataclass(repr=False)
class DataGuiComm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a les dates de trimestre ja
    existents """
    id: int
    dia: str


@dataclass(repr=False)
class DataNova:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a les dates de trimestre no
    existents
    :parameter:
    dia: Cadena de text.
    """
    dia: str
