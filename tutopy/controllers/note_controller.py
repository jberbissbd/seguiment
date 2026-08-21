from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Note, NoteNew
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.category_service import CategoryService
from tutopy.services.exceptions import DomainError
from tutopy.services.note_service import NoteService
from tutopy.ui.dialogs.note_dialog import NoteDialog
from tutopy.ui.main_window import MainWindow


class NoteController:
    """Gestiona notes i filtres entre la vista i els serveis."""

    def __init__(self, window: MainWindow, note_service: NoteService,
        category_service: CategoryService, course_service: AcademicCourseService,
        dialog_factory=NoteDialog,
        confirm_delete=None, error_handler=None):
        self.window = window
        self.view = window.student_detail.notes_tab
        self.note_service = note_service
        self.category_service = category_service
        self.course_service = course_service
        self.dialog_factory = dialog_factory
        self.confirm_delete = confirm_delete or window.confirm_note_deletion
        self.error_handler = error_handler or window.show_error
        self.current_student_id = None
        self._connect_signals()

    def start(self) -> None:
        self.refresh_options()
        self.refresh()

    def _connect_signals(self) -> None:
        self.window.student_list.student_selected.connect(self.set_student_context)
        self.window.student_list.note_create_requested.connect(
            self.create_for_student
        )
        self.view.filters_changed.connect(self.refresh)
        self.view.edit_requested.connect(self.edit)
        self.view.delete_requested.connect(self.delete)

    def refresh_options(self) -> None:
        self.view.set_options(
            self.category_service.get_all(),
            self.course_service.get_all(),
        )

    def set_student_context(self, student_id: int) -> None:
        self.current_student_id = student_id
        self.view.set_student_context(student_id)
        self.refresh()

    def refresh(self, filters=None) -> None:
        try:
            records = self.note_service.get_records(filters or self.view.filters())
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.view.set_records(records)

    def create(self) -> None:
        categories = self.category_service.get_all()
        if self.current_student_id is None:
            self.error_handler("Cal seleccionar un alumne abans d'afegir notes.")
            return
        if not categories:
            self.error_handler("Cal crear una categoria abans d'afegir notes.")
            return
        dialog = self.dialog_factory(
            parent=self.window,
            categories=categories,
            student_id=self.current_student_id,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            values = dialog.values()
            values["student_id"] = self.current_student_id
            note = self.note_service.create(NoteNew(**values))
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh_options()
        self.view.set_student_context(note.student_id)
        self.refresh()
        self._select_note(note.id)
        self.window.show_status("Nota creada correctament")

    def create_for_student(self, student_id: int) -> None:
        """Obre la creació des de l'acció contextual d'una fila d'alumne."""
        if self.current_student_id != student_id:
            self.set_student_context(student_id)
        self.create()

    def edit(self, note_id: int) -> None:
        try:
            note = self.note_service.get_by_id(note_id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        dialog = self.dialog_factory(
            parent=self.window,
            note=note,
            categories=self.category_service.get_all(),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        values["student_id"] = note.student_id
        updated = Note(id=note.id, **values)
        try:
            self.note_service.update(updated)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh_options()
        self.view.set_student_context(updated.student_id)
        self.refresh()
        self._select_note(note_id)
        self.window.show_status("Nota actualitzada correctament")

    def delete(self, note_id: int) -> None:
        if not self.confirm_delete():
            return
        try:
            self.note_service.delete(note_id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Nota eliminada correctament")

    def _select_note(self, note_id: int) -> None:
        for row in range(self.view.table.rowCount()):
            if self.view._note_id_at(row) == note_id:
                self.view.table.selectRow(row)
                return
