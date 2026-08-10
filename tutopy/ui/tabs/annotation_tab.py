from tutopy.ui.widgets.crud_views import CrudListView


class AnnotationTab(CrudListView):
    def __init__(self, parent=None):
        super().__init__("Nou descriptor", parent)
