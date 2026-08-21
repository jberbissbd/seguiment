from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox, QProgressDialog

from tutopy.models.messaging import Student, StudentNew
from tutopy.models.student_bulk import StudentBulkUpdate
from tutopy.services.exceptions import DomainError
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.student_dialog import StudentDialog
from tutopy.ui.dialogs.bulk_student_edit_dialog import BulkStudentEditDialog
from tutopy.ui.background_task import BackgroundTaskRunner
from tutopy.ui.main_window import MainWindow


class StudentController:
    """Gestiona el CRUD d'alumnes entre la vista i `StudentService`."""

    def __init__(self, window: MainWindow, service: StudentService,
        dialog_factory=StudentDialog, confirm_delete=None, error_handler=None,
        bulk_dialog_factory=BulkStudentEditDialog, task_runner=None,
        progress_dialog=QProgressDialog):
        self.window = window
        self.service = service
        self.dialog_factory = dialog_factory
        self.confirm_delete = confirm_delete or window.confirm_student_deletion
        self.error_handler = error_handler or window.show_error
        self.bulk_dialog_factory = bulk_dialog_factory
        self.task_runner = task_runner or BackgroundTaskRunner()
        self.progress_dialog = progress_dialog
        self._bulk_edit_task = None
        self._bulk_edit_progress = None
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
        view.bulk_edit_requested.connect(self.bulk_edit)

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

    def bulk_edit(self) -> None:
        """Recull i aplica una edició massiva sense bloquejar la interfície."""
        if self._bulk_edit_task is not None:
            self.window.show_status("Ja hi ha una edició massiva en curs.")
            return
        students = self.service.get_all()
        if not students:
            return
        dialog = self.bulk_dialog_factory(
            students, self.service.get_groups(), parent=self.window
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        changes = [StudentBulkUpdate(**item) for item in dialog.changes()]
        change_date = dialog.effective_date()
        progress = self.progress_dialog(
            "Actualitzant alumnes…", "Cancel·lar", 0, len(changes), self.window
        )
        progress.setWindowTitle("Edició massiva d’alumnes")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        self._bulk_edit_progress = progress

        def operation(report_progress, cancel_requested):
            return self.service.bulk_update_with_worker_connection(
                changes, change_date, progress_callback=report_progress,
                cancel_requested=cancel_requested,
            )

        self._bulk_edit_task = self.task_runner.start(
            operation,
            on_progress=self._update_bulk_progress,
            on_success=self._bulk_edit_finished,
            on_failure=self._bulk_edit_failed,
        )
        progress.canceled.connect(self._bulk_edit_task.cancel)
        progress.show()

    def _update_bulk_progress(self, completed: int, total: int) -> None:
        progress = self._bulk_edit_progress
        if progress is None:
            return
        progress.setMaximum(total)
        progress.setValue(completed)
        progress.setLabelText(f"Actualitzant alumnes… {completed} de {total}")

    def _bulk_edit_finished(self, result) -> None:
        self._close_bulk_progress()
        if result.cancelled:
            self.window.show_status("Edició massiva cancel·lada.", 5000)
            return
        self.window.student_detail.clear()
        self.refresh()
        QMessageBox.information(
            self.window, "Edició massiva completada",
            f"Alumnes actualitzats: {result.updated}\n"
            f"Sense canvis: {result.unchanged}\n"
            f"Canvis de grup: {result.group_changes}",
        )

    def _bulk_edit_failed(self, error: Exception) -> None:
        self._close_bulk_progress()
        self.error_handler(str(error))

    def _close_bulk_progress(self) -> None:
        progress = self._bulk_edit_progress
        self._bulk_edit_progress = None
        self._bulk_edit_task = None
        if progress is not None:
            progress.close()

    def _select_in_list(self, student_id: int) -> None:
        for row in range(self.window.student_list.list_widget.count()):
            item = self.window.student_list.list_widget.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == student_id:
                self.window.student_list.list_widget.setCurrentItem(item)
                return
