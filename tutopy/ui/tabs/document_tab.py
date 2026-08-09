from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton

from tutopy.ui.widgets.crud_views import CrudTableView


class DocumentTab(CrudTableView):
    open_requested = Signal(int)
    export_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(["Nom", "Descripció", "Fitxer"], "Nou document", parent)
        self.open_button = QPushButton("Obrir")
        self.open_button.setObjectName("secondaryButton")
        self.export_button = QPushButton("Exportar…")
        self.export_button.setObjectName("secondaryButton")
        self.actions.layout().insertWidget(1, self.open_button)
        self.actions.layout().insertWidget(2, self.export_button)
        self.open_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.open_button.clicked.connect(self._open)
        self.export_button.clicked.connect(self._export)

    def _selection_changed(self):
        super()._selection_changed()
        selected = self.current_id() is not None
        self.open_button.setEnabled(selected)
        self.export_button.setEnabled(selected)

    def _open(self):
        if self.current_id() is not None:
            self.open_requested.emit(self.current_id())

    def _export(self):
        if self.current_id() is not None:
            self.export_requested.emit(self.current_id())
