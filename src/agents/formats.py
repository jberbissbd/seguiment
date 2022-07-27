from dataclasses import dataclass
from datetime import date


@dataclass
class Registre_sortida:
    id: int
    alumne: str
    categoria: str
    data: str
    descripcio: str

@dataclass
class Registre_entrada:
    alumne: str
    categoria: str
    data: str
    descripcio: str


@dataclass
class Alumne:
    nom: str


@dataclass
class Categoria:
    id: int
    nom: str


@dataclass
class Data:
    id: int
    dia: str
