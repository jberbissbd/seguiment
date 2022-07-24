from dataclasses import dataclass


@dataclass
class Registre:
    id: int
    alumne: str
    categoria: str
    data: str
    descripcio: str


@dataclass
class Alumne:
    id: int
    nom: str


@dataclass
class Categoria:
    id: int
    nom: str


@dataclass
class Data:
    id: int
    dia: str
