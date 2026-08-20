import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QInputDialog, QLineEdit, QMessageBox, QProgressDialog,
)

from tutopy.services.bulk_import_service import BulkImportService
from tutopy.services.data_management_service import DataManagementService
from tutopy.services.exceptions import DomainError
from tutopy.ui.dialogs.clear_data_dialog import ClearDataDialog
from tutopy.ui.dialogs.import_conflicts_dialog import ImportConflictsDialog
from tutopy.ui.dialogs.transfer_conflicts_dialog import TransferConflictsDialog
from tutopy.ui.dialogs.transfer_student_selection_dialog import (
    TransferStudentSelectionDialog,
)
from tutopy.ui.main_window import MainWindow
from tutopy.ui.background_task import BackgroundTaskRunner


LOGGER = logging.getLogger(__name__)


class DataManagementController:
    def __init__(self, window: MainWindow, importer: BulkImportService,
                 data_service: DataManagementService, transfer_service=None,
                 student_service=None,
                 on_changed=None,
                 conflict_dialog=ImportConflictsDialog,
                 clear_dialog=ClearDataDialog,
                 transfer_conflict_dialog=TransferConflictsDialog,
                 transfer_selection_dialog=TransferStudentSelectionDialog,
                 task_runner=None, progress_dialog=QProgressDialog):
        self.window = window
        self.importer = importer
        self.data_service = data_service
        self.transfer_service = transfer_service
        self.student_service = student_service
        self.on_changed = on_changed or (lambda: None)
        self.conflict_dialog = conflict_dialog
        self.clear_dialog = clear_dialog
        self.transfer_conflict_dialog = transfer_conflict_dialog
        self.transfer_selection_dialog = transfer_selection_dialog
        self.task_runner = task_runner or BackgroundTaskRunner()
        self.progress_dialog = progress_dialog
        self._transfer_export_task = None
        self._transfer_progress = None
        view = window.data_tools
        view.template_requested.connect(self.export_template)
        view.import_requested.connect(self.import_spreadsheet)
        view.clear_requested.connect(self.clear_all)
        view.transfer_student_requested.connect(self.export_selected_student)
        view.transfer_all_requested.connect(self.export_all_students)
        view.transfer_import_requested.connect(self.import_transfer)

    def export_selected_student(self) -> None:
        """Exporta l'agregat de l'alumne seleccionat a un paquet portable."""
        students = self.student_service.get_all() if self.student_service else []
        if not students:
            self.window.show_error("No hi ha alumnes disponibles per exportar.")
            return
        dialog = self.transfer_selection_dialog(students, self.window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        student_ids = dialog.student_ids()
        self._export_transfer(student_ids, "alumnes-seleccionats.tpy")

    def export_all_students(self) -> None:
        """Exporta tots els agregats de la instància."""
        students = self.student_service.get_all() if self.student_service else []
        if not students:
            self.window.show_error("No hi ha alumnes disponibles per exportar.")
            return
        self._export_transfer(
            [student.id for student in students], "tutopy-complet.tpy"
        )

    def _export_transfer(self, student_ids, default_name) -> None:
        if self.transfer_service is None:
            self.window.show_error("El servei de transferència no està disponible.")
            return
        if self._transfer_export_task is not None:
            self.window.show_status("Ja hi ha una transferència en curs.")
            return
        filename, _ = QFileDialog.getSaveFileName(
            self.window, "Exportar paquet Tutopy", default_name,
            "Paquet Tutopy (*.tpy)",
        )
        if not filename:
            return
        password = self._new_transfer_password()
        if password is None:
            return
        try:
            preparation = self.transfer_service.prepare_export(
                student_ids, filename, password
            )
        except Exception as error:
            self._show_operation_error(error, "exportar el paquet")
            return
        progress = self.progress_dialog(
            "Preparant el paquet…", "Cancel·lar", 0, len(student_ids), self.window
        )
        progress.setWindowTitle("Exportació de transferència")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        self._transfer_progress = progress

        def operation(report_progress, cancel_requested):
            return self.transfer_service.export_prepared(
                preparation, progress_callback=report_progress,
                cancel_requested=cancel_requested,
            )

        self._transfer_export_task = self.task_runner.start(
            operation,
            on_progress=self._update_transfer_progress,
            on_success=self._transfer_export_finished,
            on_failure=self._transfer_export_failed,
        )
        progress.canceled.connect(self._transfer_export_task.cancel)
        progress.show()

    def _update_transfer_progress(self, completed: int, total: int) -> None:
        progress = self._transfer_progress
        if progress is None:
            return
        progress.setMaximum(total)
        progress.setValue(completed)
        label = (
            "Comprimint i xifrant el paquet…"
            if completed == total
            else f"Preparant alumnes… {completed} de {total}"
        )
        progress.setLabelText(label)

    def _transfer_export_finished(self, path) -> None:
        self._close_transfer_progress()
        if path is None:
            self.window.show_status("Exportació de transferència cancel·lada.", 5000)
            return
        self.window.show_status(f"Paquet desat a {path}", 5000)

    def _transfer_export_failed(self, error: Exception) -> None:
        self._close_transfer_progress()
        self._show_operation_error(error, "exportar el paquet")

    def _close_transfer_progress(self) -> None:
        progress = self._transfer_progress
        self._transfer_progress = None
        self._transfer_export_task = None
        if progress is not None:
            progress.close()

    def import_transfer(self) -> None:
        """Analitza, resol conflictes i importa un paquet `.tpy`."""
        if self.transfer_service is None:
            self.window.show_error("El servei de transferència no està disponible.")
            return
        filename, _ = QFileDialog.getOpenFileName(
            self.window, "Importar paquet Tutopy", "",
            "Paquet Tutopy (*.tpy)",
        )
        if not filename:
            return
        password = self._transfer_password()
        if password is None:
            return
        try:
            preview = self.transfer_service.analyze(filename, password)
            decisions = ()
            if preview.conflicts:
                dialog = self.transfer_conflict_dialog(
                    preview.conflicts, self.window
                )
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                decisions = dialog.decisions()
            result = self.transfer_service.execute(
                preview, decisions, password=password
            )
        except Exception as error:
            self._show_operation_error(error, "importar el paquet")
            return
        self.on_changed()
        QMessageBox.information(
            self.window, "Transferència completada",
            f"Alumnes creats: {result.created}\n"
            f"Alumnes substituïts: {result.replaced}\n"
            f"Alumnes conservats: {result.skipped}\n"
            f"Importats com a nous: {result.imported_as_new}\n"
            f"Documents importats: {result.documents}",
        )

    def _new_transfer_password(self) -> str | None:
        """Demana dues vegades la contrasenya d'un paquet nou."""
        password = self._transfer_password("Protegir paquet Tutopy")
        if password is None:
            return None
        confirmation, accepted = QInputDialog.getText(
            self.window, "Confirmar contrasenya",
            "Torna a escriure la contrasenya:", QLineEdit.EchoMode.Password,
        )
        if not accepted:
            return None
        if password != confirmation:
            self.window.show_error("Les contrasenyes no coincideixen.")
            return None
        if len(password) < 8:
            self.window.show_error(
                "La contrasenya ha de tenir com a mínim 8 caràcters."
            )
            return None
        return password

    def _transfer_password(
        self, title: str = "Obrir paquet Tutopy",
    ) -> str | None:
        """Demana una contrasenya sense mostrar-ne els caràcters."""
        password, accepted = QInputDialog.getText(
            self.window, title, "Contrasenya del paquet:",
            QLineEdit.EchoMode.Password,
        )
        return password if accepted else None

    def _show_operation_error(self, error: Exception, operation: str) -> None:
        """Mostra un motiu útil i registra el detall tècnic inesperat."""
        if isinstance(error, DomainError):
            message = str(error)
        elif isinstance(error, OSError):
            reason = error.strerror or str(error)
            message = f"No s’ha pogut {operation}: {reason}."
        else:
            LOGGER.exception("Error inesperat en intentar %s", operation)
            message = (
                f"No s’ha pogut {operation} per un error intern inesperat "
                f"({type(error).__name__}). Consulteu el registre de l’aplicació."
            )
        self.window.show_error(message)

    def export_template(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self.window, "Desar plantilla", "plantilla_tutopy.xlsx",
            "Full de càlcul Excel (*.xlsx)",
        )
        if not filename:
            return
        try:
            path = self.importer.create_template(filename)
        except (DomainError, OSError) as error:
            self.window.show_error(str(error))
            return
        self.window.show_status(f"Plantilla desada a {path}", 5000)

    def import_spreadsheet(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self.window, "Importar dades", "",
            "Fulls de càlcul (*.xlsx *.ods);;Excel (*.xlsx);;OpenDocument (*.ods)"
        )
        if not filename:
            return
        try:
            preview = self.importer.analyze(filename)
            if preview.issues:
                self.window.show_import_issues(preview.issues)
                return
            decisions = ()
            if preview.conflicts:
                dialog = self.conflict_dialog(preview.conflicts, self.window)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                decisions = dialog.decisions()
            result = self.importer.execute(preview, decisions)
        except (DomainError, OSError) as error:
            self.window.show_error(str(error))
            return
        self.on_changed()
        QMessageBox.information(
            self.window, "Importació completada",
            f"Alumnes creats: {result.students_created}\n"
            f"Alumnes actualitzats: {result.students_updated}\n"
            f"Files omeses: {result.students_skipped}\n"
            f"Categories creades: {result.categories_created}\n"
            f"Categories reutilitzades: {result.categories_reused}",
        )

    def clear_all(self) -> None:
        dialog = self.clear_dialog(self.window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            result = self.data_service.delete_all()
        except DomainError as error:
            self.window.show_error(str(error))
            return
        self.on_changed()
        message = "S’han eliminat totes les dades."
        if result.file_warnings:
            message += "\n\nNo s’han pogut eliminar alguns fitxers:\n" + "\n".join(result.file_warnings)
        QMessageBox.information(self.window, "Dades eliminades", message)
