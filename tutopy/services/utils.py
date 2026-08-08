import os
import sys

def get_app_dir() -> str:
    """Retorna el directori on es troba l'executable o el script principal.

    Funciona tant en desenvolupament com en executables PyInstaller (--onefile).
    """
    if getattr(sys, "frozen", False):
        # PyInstaller bundle
        return os.path.dirname(sys.executable)
    # Desenvolupament: directori del projecte (arrel)
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class DateConverter():
    """Classe per a convertir dates entre formats"""
    def iso_to_display(self, iso_date: str):
        """Converteix dates del format YYYY-MM-DD a DD/MM/YYYY"""
        if not isinstance(iso_date, str):
            raise ValueError("L'input de la funció ha de ser una cadena de"
                             "text")
        elements_display = tuple(iso_date.split("-"))
        return f"{elements_display[2]}/{elements_display[1]}/{elements_display[0]}"

    def display_to_iso(self, iso_date: str):
        """Converteix dates del format DD/MM/YYYY a YYYY-MM-DD"""
        if not isinstance(iso_date, str):
            raise ValueError("L'input de la funció ha de ser una cadena de"
                             "text")
        data_conversio = tuple(iso_date.split("/"))
        return f"{data_conversio[2]}-{data_conversio[1]}-{data_conversio[0]}"

class AcademicCourseDeterminator():
    """Determina el curs acadèmic"""

    def curs_academic_singular(self,date: str) -> str:
        """Determina el curs acadèmic a partir d'una data ISO.

        El curs va de setembre a agost (ex: 2026-05-14 → 2025-2026).

        Args:
            date_str: Data en format ``YYYY-MM-DD``.

        Returns:
            Curs acadèmic en format ``"YYYY-YYYY"``, o cadena buida si
            el format no és vàlid.
        """
        parts_curs = date.split("-")
        year, month = int(parts_curs[0]),int(parts_curs[1])
        if month>=9:
            return f"{year}-{year+1}"
        return f"{year-1}-{year}"
