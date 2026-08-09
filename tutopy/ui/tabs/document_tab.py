from tutopy.ui.widgets.crud_views import CrudTableView


class DocumentTab(CrudTableView):
    def __init__(self, parent=None):
        super().__init__(["Nom", "Descripció", "Fitxer"], "Nou document", parent)
