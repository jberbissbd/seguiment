from tutopy.ui.widgets.crud_views import CrudTableView


class ContactTab(CrudTableView):
    def __init__(self, parent=None):
        super().__init__(["Nom", "Relació", "Telèfon", "Correu"], "Nou contacte", parent)
