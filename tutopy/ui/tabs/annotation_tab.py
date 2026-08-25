"""Pestanya de descriptors de l'alumne (CRUD sobre una llista simple)."""

from tutopy.ui.widgets.crud_views import CrudListView


class AnnotationTab(CrudListView):
    """Llista de descriptors de l'alumne seleccionat."""

    def __init__(self, parent=None):
        """Configura la vista CRUD amb el text "Nou descriptor"."""
        super().__init__("Nou descriptor", parent)
