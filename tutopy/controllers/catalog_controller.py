"""Controladors dels catàlegs editables de la barra lateral (categories).

Connecta les peticions de creació, edició i eliminació de la vista de
catàleg amb `CategoryService`, delegant el comportament comú de CRUD a
`_CatalogController`.
"""

from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Category, CategoryNew
from tutopy.services.category_service import CategoryService
from tutopy.services.exceptions import DomainError
from tutopy.ui.dialogs.text_value_dialog import TextValueDialog
from tutopy.ui.main_window import MainWindow


class _CatalogController:
    """Comportament comú dels catàlegs editables de la barra lateral."""

    entity_label = "element"
    create_status = "Element creat"
    update_status = "Element actualitzat"
    delete_status = "Element eliminat"

    def __init__(self, window: MainWindow, service, view, dialog_factory=TextValueDialog,
        confirm_delete=None, error_handler=None, on_changed=None):
        self.window = window
        self.service = service
        self.view = view
        self.dialog_factory = dialog_factory
        self.confirm_delete = confirm_delete or window.confirm_deletion
        self.error_handler = error_handler or window.show_error
        self.on_changed = on_changed
        self.view.create_requested.connect(self.create)
        self.view.edit_requested.connect(self.edit)
        self.view.delete_requested.connect(self.delete)

    def start(self):
        """Inicia el controlador carregant els elements del catàleg a la vista."""
        self.refresh()

    def refresh(self):
        """Actualitza la vista amb els elements actuals retornats pel servei."""
        self.view.set_items([(item.id, self._text(item)) for item in self.service.get_all()])

    def create(self):
        """Obre el diàleg de creació i desa el nou element si s'accepta."""
        dialog = self._dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self._create(dialog.value()), self.create_status)

    def edit(self, entity_id):
        """Obre el diàleg d'edició per a `entity_id` i desa els canvis si s'accepten."""
        entity = self.service.get_by_id(entity_id)
        if entity is None:
            self.error_handler(f"No s'ha trobat {self.entity_label}.")
            return
        dialog = self._dialog(self._text(entity))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self._update(entity_id, dialog.value()), self.update_status)

    def delete(self, entity_id):
        """Elimina `entity_id` del catàleg prèvia confirmació de l'usuari."""
        if self.confirm_delete(self.entity_label):
            self._run(lambda: self.service.delete(entity_id), self.delete_status)

    def _run(self, operation, status):
        """Executa `operation`, gestiona errors de domini i notifica l'usuari."""
        try:
            operation()
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        if self.on_changed:
            self.on_changed()
        self.window.show_status(status)


class CategoryController(_CatalogController):
    """Gestiona el catàleg de categories mostrat a la barra lateral."""

    entity_label = "aquesta categoria"
    create_status = "Categoria creada"
    update_status = "Categoria actualitzada"
    delete_status = "Categoria eliminada"

    def __init__(self, window: MainWindow, service: CategoryService, **kwargs):
        """Configura el controlador sobre la vista de categories de la finestra."""
        super().__init__(window, service, window.category_view, **kwargs)

    def _dialog(self, value=""):
        return self.dialog_factory(
            parent=self.window, title="Categoria", label="Nom:", value=value
        )

    @staticmethod
    def _text(category):
        return category.name

    def _create(self, value):
        return self.service.create(CategoryNew(value))

    def _update(self, entity_id, value):
        return self.service.rename(Category(entity_id, value))
