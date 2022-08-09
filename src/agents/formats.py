from dataclasses import dataclass


@dataclass(repr=False)
class Registres_gui_comm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a registres ja existents"""
    id: int
    alumne: dataclass
    categoria: dataclass
    data: str
    descripcio: str


@dataclass(repr=False)
class Registres_bbdd_comm:
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
class Alumne_nou:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a alumnes nous"""
    nom: str


@dataclass(repr=False)
class Categoria_comm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a categories ja existents"""
    id: int
    nom: str


@dataclass(repr=False)
class Data_gui_comm:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a les dates de trimestre ja
    existents """
    id: int
    dia: str


@dataclass(repr=False)
class Data_nova:
    """Classe per a la missatgeria entre els agents i la interficie grafica, per a les dates de trimestre no
    existents
    :parameter:
    dia: Cadena de text.
    """
    dia: str
