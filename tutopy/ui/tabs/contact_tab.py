"""Pestanya de contactes de l'alumne (CRUD sobre una taula)."""

from tutopy.ui.widgets.crud_views import CrudTableView


class ContactTab(CrudTableView):
    """Taula de contactes (nom, relació, telèfon i correu) de l'alumne."""

    def __init__(self, parent=None):
        """Configura la taula amb les columnes de contacte i el text "Nou contacte"."""
        super().__init__(["Nom", "Relació", "Telèfon", "Correu"], "Nou contacte", parent)
