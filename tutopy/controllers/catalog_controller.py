from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import (
    AcademicCourse, AcademicCourseNew, Category, CategoryNew,
)
from tutopy.services.academic_course_service import AcademicCourseService
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
        self.refresh()

    def refresh(self):
        self.view.set_items([(item.id, self._text(item)) for item in self.service.get_all()])

    def create(self):
        dialog = self._dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self._create(dialog.value()), self.create_status)

    def edit(self, entity_id):
        entity = self.service.get_by_id(entity_id)
        if entity is None:
            self.error_handler(f"No s'ha trobat {self.entity_label}.")
            return
        dialog = self._dialog(self._text(entity))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self._update(entity_id, dialog.value()), self.update_status)

    def delete(self, entity_id):
        if self.confirm_delete(self.entity_label):
            self._run(lambda: self.service.delete(entity_id), self.delete_status)

    def _run(self, operation, status):
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
    entity_label = "aquesta categoria"
    create_status = "Categoria creada"
    update_status = "Categoria actualitzada"
    delete_status = "Categoria eliminada"

    def __init__(self, window: MainWindow, service: CategoryService, **kwargs):
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


class AcademicCourseController(_CatalogController):
    entity_label = "aquest curs acadèmic"
    create_status = "Curs acadèmic creat"
    update_status = "Curs acadèmic actualitzat"
    delete_status = "Curs acadèmic eliminat"

    def __init__(self, window: MainWindow, service: AcademicCourseService, **kwargs):
        super().__init__(window, service, window.course_view, **kwargs)

    def _dialog(self, value=""):
        return self.dialog_factory(
            parent=self.window, title="Curs acadèmic",
            label="Curs (AAAA-AAAA):", value=value,
        )

    @staticmethod
    def _text(course):
        return course.course

    def _create(self, value):
        return self.service.create(AcademicCourseNew(value))

    def _update(self, entity_id, value):
        return self.service.update(AcademicCourse(entity_id, value))
