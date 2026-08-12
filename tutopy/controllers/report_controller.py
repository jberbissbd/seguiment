import re

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.models.reporting import TermConfigurationNew
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.exceptions import DomainError
from tutopy.services.report_configuration_service import ReportConfigurationService
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService
from tutopy.services.word_report_service import WordReportService
from tutopy.services.student_export_service import StudentExportService
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.report_export_dialog import ReportExportDialog
from tutopy.ui.dialogs.term_configuration_dialog import TermConfigurationDialog
from tutopy.ui.dialogs.batch_export_dialog import BatchExportDialog
from tutopy.ui.main_window import MainWindow


class ReportController:
    def __init__(self, window: MainWindow, students: StudentService,
                 courses: AcademicCourseService,
                 configuration: ReportConfigurationService,
                 reports: SpreadsheetReportService,
                 word_reports: WordReportService,
                 student_exports: StudentExportService,
                 term_dialog=TermConfigurationDialog,
                 export_dialog=ReportExportDialog,
                 batch_export_dialog=BatchExportDialog,
                 error_handler=None, confirm_delete=None):
        self.window = window
        self.students = students
        self.courses = courses
        self.configuration = configuration
        self.reports = reports
        self.word_reports = word_reports
        self.student_exports = student_exports
        self.term_dialog = term_dialog
        self.export_dialog = export_dialog
        self.batch_export_dialog = batch_export_dialog
        self.error_handler = error_handler or window.show_error
        self.confirm_delete = confirm_delete or window.confirm_deletion
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
        self.refresh()

    def refresh(self) -> None:
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
        try:
            self.configuration.clear_header_image()
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh()
        self.window.show_status("Logotip dels informes eliminat")

    def create_term_configuration(self) -> None:
        self._open_term_dialog()

    def edit_term_configuration(self, configuration_id: int) -> None:
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
        if export_format == "docx":
            default_name = f"informe_{safe_name}.docx"
            file_filter = "Document de text Word (*.docx)"
        else:
            default_name = f"informe_{safe_name}.xlsx"
            file_filter = "Full de càlcul Excel (*.xlsx)"
        filename, _ = QFileDialog.getSaveFileName(
            self.window, "Desar informe", default_name, file_filter,
        )
        if not filename:
            return
        try:
            self.configuration.set_category_order(dialog.category_order())
            if export_format == "docx":
                path = self.word_reports.export_student(student_id, filename)
            else:
                path = self.reports.export_student(
                    student_id, filename, include_terms=dialog.include_terms.isChecked()
                )
        except (DomainError, OSError) as error:
            self.error_handler(str(error))
            return
        self.window.show_status(f"Informe desat a {path}", 5000)

    def export_students(self) -> None:
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
            result = self.student_exports.export_students(
                dialog.student_ids(), directory, dialog.export_format(),
                include_terms=dialog.include_terms.isChecked(),
                include_documents=dialog.include_documents.isChecked(),
            )
        except (DomainError, OSError) as error:
            self.error_handler(str(error))
            return
        message = f"Alumnes exportats: {result.exported}"
        if result.failures:
            message += f"\nErrors: {len(result.failures)}\n\n" + "\n".join(
                f"{failure.student_name}: {failure.reason}"
                for failure in result.failures
            )
        QMessageBox.information(self.window, "Exportació completada", message)
        self.window.show_status(f"Exportació desada a {result.destination}", 5000)

    @staticmethod
    def _display_date(value: str) -> str:
        year, month, day = value.split("-")
        return f"{day}/{month}/{year}"
