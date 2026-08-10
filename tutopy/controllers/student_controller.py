from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from tutopy.models.messaging import Student, StudentNew
from tutopy.services.exceptions import DomainError
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.student_dialog import StudentDialog
from tutopy.ui.main_window import MainWindow


class StudentController:
    """Gestiona el CRUD d'alumnes entre la vista i `StudentService`."""

    def __init__(self, window: MainWindow, service: StudentService,
        dialog_factory=StudentDialog, confirm_delete=None, error_handler=None):
        self.window = window
        self.service = service
        self.dialog_factory = dialog_factory
        self.confirm_delete = confirm_delete or window.confirm_student_deletion
        self.error_handler = error_handler or window.show_error
        self._connect_signals()

    def start(self) -> None:
        self.refresh()

    def _connect_signals(self) -> None:
        view = self.window.student_list
        view.search_changed.connect(self.search)
        view.student_selected.connect(self.select)
        view.create_requested.connect(self.create)
        view.edit_requested.connect(self.edit)
        view.delete_requested.connect(self.delete)

    def refresh(self) -> None:
        students = self.service.get_all()
        self.window.student_list.set_students(students)
        self.window.show_status(f"{len(students)} alumnes")

    def search(self, query: str) -> None:
        self.window.student_list.set_students(self.service.search(query))

    def select(self, student_id: int) -> None:
        self.window.student_detail.show_student(self.service.get_by_id(student_id))

    def create(self) -> None:
        dialog = self.dialog_factory(
            parent=self.window, groups=self.service.get_groups()
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        try:
            student = self.service.create(StudentNew(**values))
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self._select_in_list(student.id)
        self.window.show_status("Alumne creat correctament")

    def edit(self, student_id: int) -> None:
        student = self.service.get_by_id(student_id)
        if student is None:
            return
        dialog = self.dialog_factory(
            parent=self.window, student=student, groups=self.service.get_groups()
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        updated = Student(
            id=student.id,
            uuid=student.uuid,
            name=values["name"],
            surnames=values["surnames"],
            group_name=values["group_name"],
        )
        try:
            self.service.update(updated)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self._select_in_list(student_id)
        self.window.show_status("Alumne actualitzat correctament")

    def delete(self, student_id: int) -> None:
        student = self.service.get_by_id(student_id)
        if student is None or not self.confirm_delete(student.full_name):
            return
        try:
            self.service.delete(student_id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.window.student_detail.clear()
        self.refresh()
        self.window.show_status("Alumne eliminat correctament")

    def _select_in_list(self, student_id: int) -> None:
        for row in range(self.window.student_list.list_widget.count()):
            item = self.window.student_list.list_widget.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == student_id:
                self.window.student_list.list_widget.setCurrentItem(item)
                return
