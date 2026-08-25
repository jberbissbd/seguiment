"""Controlador d'informes: configuració, logotip, ordre de categories i exportació.

Orquestra `ReportConfigurationService`, `ReportFileService` i
`StudentExportService`, delegant l'exportació massiva a
`BackgroundOperationPresenter` perquè no bloquegi la interfície.
"""

import re

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QProgressDialog

from tutopy.models.reporting import TermConfigurationNew
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.exceptions import DomainError
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.report_file_service import ReportFileService
from tutopy.services.student_export_service import StudentExportService
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.report_export_dialog import ReportExportDialog
from tutopy.ui.dialogs.term_configuration_dialog import TermConfigurationDialog
from tutopy.ui.dialogs.batch_export_dialog import BatchExportDialog
from tutopy.ui.main_window import MainWindow
from tutopy.ui.background_task import BackgroundOperationPresenter, BackgroundTaskRunner


class ReportController:
    """Gestiona la configuració i l'exportació d'informes d'alumnes."""

    def __init__(self, window: MainWindow, students: StudentService,
                 courses: AcademicCourseService,
                 configuration: ReportConfigurationService,
                 report_files: ReportFileService,
                 student_exports: StudentExportService,
                 term_dialog=TermConfigurationDialog,
                 export_dialog=ReportExportDialog,
                 batch_export_dialog=BatchExportDialog,
                 error_handler=None, confirm_delete=None,
                 task_runner=None, progress_dialog=QProgressDialog):
        """Desa les dependències i connecta les accions d'informes de la vista."""
        self.window = window
        self.students = students
        self.courses = courses
        self.configuration = configuration
        self.report_files = report_files
        self.student_exports = student_exports
        self.term_dialog = term_dialog
        self.export_dialog = export_dialog
        self.batch_export_dialog = batch_export_dialog
        self.error_handler = error_handler or window.show_error
        self.confirm_delete = confirm_delete or window.confirm_deletion
        self.task_runner = task_runner or BackgroundTaskRunner()
        self.progress_dialog = progress_dialog
        self._batch_export = BackgroundOperationPresenter(
            self.window, self.task_runner, self.progress_dialog
        )
        view = window.data_tools
        view.category_order_requested.connect(self.configure_category_order)
        view.report_logo_requested.connect(self.configure_report_logo)
        view.report_logo_remove_requested.connect(self.remove_report_logo)
        view.term_create_requested.connect(self.create_term_configuration)
        view.term_edit_requested.connect(self.edit_term_configuration)
        view.term_delete_requested.connect(self.delete_term_configuration)
        window.student_detail.export_requested.connect(self.export_student)
        window.student_list.batch_export_requested.connect(self.export_students)

    def start(self) -> None:
        """Carrega les configuracions de trimestres i el logotip a la vista."""
        self.refresh()

    def refresh(self) -> None:
        """Actualitza la taula de configuracions de trimestres i el logotip mostrats."""
        course_names = {course.id: course.course for course in self.courses.get_all()}
        rows = []
        for configuration in self.configuration.get_term_configurations():
            rows.append((configuration.id, (
                course_names.get(configuration.academic_course_id, "—"),
                configuration.group_name,
                self._display_date(configuration.second_term_start),
                self._display_date(configuration.third_term_start),
            )))
        self.window.data_tools.set_term_configurations(rows)
        logo = self.configuration.get_header_image()
        self.window.data_tools.set_report_logo(logo.name if logo else None)

    def configure_report_logo(self) -> None:
        """Selecciona i desa una imatge com a logotip dels informes."""
        filename, _ = QFileDialog.getOpenFileName(
            self.window, "Seleccionar logotip dels informes", "",
            "Imatges (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff)",
        )
        if not filename:
            return
        try:
            self.configuration.set_header_image(filename)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Logotip dels informes desat")

    def remove_report_logo(self) -> None:
        """Elimina el logotip configurat per als informes."""
        try:
            self.configuration.clear_header_image()
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Logotip dels informes eliminat")

    def create_term_configuration(self) -> None:
        """Obre el diàleg per crear una nova configuració de trimestres."""
        self._open_term_dialog()

    def edit_term_configuration(self, configuration_id: int) -> None:
        """Obre el diàleg d'edició per a una configuració de trimestres existent.

        Args:
            configuration_id: Identificador de la configuració a editar.
        """
        configuration = next((item for item in self.configuration.get_term_configurations()
                              if item.id == configuration_id), None)
        if configuration is None:
            self.error_handler("No s’ha trobat la configuració de trimestres.")
            return
        self._open_term_dialog(configuration)

    def _open_term_dialog(self, configuration=None) -> None:
        groups = list(self.students.get_groups())
        if configuration is not None and configuration.group_name not in groups:
            groups.append(configuration.group_name)
        dialog = self.term_dialog(
            self.courses.get_all(), sorted(groups), configuration,
            parent=self.window,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.configuration.save_term_configuration(
                TermConfigurationNew(**dialog.values())
            )
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Configuració de trimestres desada")

    def delete_term_configuration(self, configuration_id: int) -> None:
        """Elimina una configuració de trimestres prèvia confirmació de l'usuari.

        Args:
            configuration_id: Identificador de la configuració a eliminar.
        """
        if not self.confirm_delete("aquesta configuració de trimestres"):
            return
        try:
            self.configuration.delete_term_configuration(configuration_id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Configuració de trimestres eliminada")

    def configure_category_order(self) -> None:
        """Obre el diàleg per definir l'ordre de les categories als informes."""
        dialog = self.export_dialog(
            self.configuration.get_ordered_categories(), parent=self.window,
            show_term_option=False,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.configuration.set_category_order(dialog.category_order())
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.window.show_status("Ordre de categories desat")

    def export_student(self, student_id: int) -> None:
        """Genera i desa l'informe d'un alumne, opcionalment amb els seus documents.

        Args:
            student_id: Identificador de l'alumne a exportar.
        """
        student = self.students.get_by_id(student_id)
        if student is None:
            self.error_handler("No s’ha trobat l’alumne.")
            return
        dialog = self.export_dialog(
            self.configuration.get_ordered_categories(), parent=self.window,
            show_term_option=True,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        safe_name = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]+', "_", student.filing_name
        ).strip(" ._")
        export_format = dialog.export_format()
        try:
            format_details = self.report_files.get_format(export_format)
        except DomainError as error:
            self.error_handler(str(error))
            return
        if dialog.include_documents.isChecked():
            directory = QFileDialog.getExistingDirectory(
                self.window, "Seleccionar carpeta d’exportació"
            )
            if not directory:
                return
            try:
                self.configuration.set_category_order(dialog.category_order())
                path = self.student_exports.export_student(
                    student_id, directory, export_format,
                    include_terms=dialog.include_terms.isChecked(),
                )
            except (DomainError, OSError) as error:
                self.error_handler(str(error))
                return
            self.window.show_status(f"Informe i documents desats a {path}", 5000)
            return
        label, extension = format_details.label, format_details.extension
        default_name = f"informe_{safe_name}.{extension}"
        file_filter = f"{label} (*.{extension})"
        filename, _ = QFileDialog.getSaveFileName(
            self.window, "Desar informe", default_name, file_filter,
        )
        if not filename:
            return
        try:
            self.configuration.set_category_order(dialog.category_order())
            path = self.report_files.export_student(
                student_id, filename, export_format,
                include_terms=dialog.include_terms.isChecked(),
            )
        except (DomainError, OSError) as error:
            self.error_handler(str(error))
            return
        self.window.show_status(f"Informe desat a {path}", 5000)

    def export_students(self) -> None:
        """Exporta els informes d'un lot d'alumnes sense bloquejar la interfície."""
        if self._batch_export.is_running():
            self.window.show_status("Ja hi ha una exportació en curs.")
            return
        dialog = self.batch_export_dialog(
            self.students.get_all(), self.configuration.get_ordered_categories(),
            parent=self.window,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        directory = QFileDialog.getExistingDirectory(
            self.window, "Seleccionar carpeta d’exportació"
        )
        if not directory:
            return
        try:
            self.configuration.set_category_order(dialog.category_order())
            preparation = self.student_exports.prepare_students_export(
                dialog.student_ids(), directory, dialog.export_format(),
                include_terms=dialog.include_terms.isChecked(),
                include_documents=dialog.include_documents.isChecked(),
            )
        except (DomainError, OSError) as error:
            self.error_handler(str(error))
            return
        def operation(report_progress, cancel_requested):
            return self.student_exports.export_prepared(
                preparation, progress_callback=report_progress,
                cancel_requested=cancel_requested,
            )

        self._batch_export.start(
            operation,
            title="Exportació d’informes",
            label="Preparant els informes…",
            maximum=len(preparation.student_ids),
            on_success=self._batch_export_finished,
            on_failure=self._batch_export_failed,
            progress_label=lambda completed, total:
                f"Generant informes… {completed} de {total}",
        )

    def _batch_export_finished(self, result) -> None:
        message = f"Alumnes exportats: {result.exported}"
        if result.cancelled:
            message = "Exportació cancel·lada.\n" + message
        if result.failures:
            message += f"\nErrors: {len(result.failures)}\n\n" + "\n".join(
                f"{failure.student_name}: {failure.reason}"
                for failure in result.failures
            )
        QMessageBox.information(self.window, "Exportació completada", message)
        self.window.show_status(f"Exportació desada a {result.destination}", 5000)

    def _batch_export_failed(self, error: Exception) -> None:
        self.error_handler(str(error))

    @staticmethod
    def _display_date(value: str) -> str:
        year, month, day = value.split("-")
        return f"{day}/{month}/{year}"
