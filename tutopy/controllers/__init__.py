"""
Paquet de controladors de l'aplicació.

Aquest paquet conté tots els controladors que actuen com a mediadors
entre la vista i els serveis.
"""

from .student_controller import StudentController

__all__ = [
    "StudentController",
]
