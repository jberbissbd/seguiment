

class DateConverter():
    """Classe per a convertir dates entre formats"""
    def iso_to_display(self, iso_date: str):
        """Converteix dates del format YYYY-MM-DD a DD/MM/YYYY"""
        if isinstance(iso_date, str) is False:
            raise ValueError("L'input de la funció ha de ser una cadena de"
                             "text")
        elements_display = tuple(iso_date.split("-"))
        return f"{elements_display[2]}/{elements_display[1]}/{elements_display[0]}"

    def display_to_iso(self, iso_date: str):
        """Converteix dates del format DD/MM/YYYY a YYYY-MM-DD"""
        if isinstance(iso_date, str) is False:
            raise ValueError("L'input de la funció ha de ser una cadena de"
                             "text")
        data_conversio = tuple(iso_date.split("/"))
        return f"{data_conversio[2]}-{data_conversio[1]}-{data_conversio[0]}"
