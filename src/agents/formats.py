from dataclasses import dataclass
from datetime import date


@dataclass
class Registres_gui_input:
    id: int
    alumne: dataclass
    categoria: str
    data: str
    descripcio: str

@dataclass
class Registres_gui_output:
    alumne: dataclass
    categoria: str
    data: str
    descripcio: str


@dataclass
class Alumne_gui_input:
    id: int
    nom: str


@dataclass
class Categoria_gui_input:
    id: int
    nom: str


@dataclass
class Data_gui_input:
    id: int
    dia: str
