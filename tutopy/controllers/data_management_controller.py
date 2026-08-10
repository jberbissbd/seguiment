from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.services.bulk_import_service import BulkImportService
from tutopy.services.data_management_service import DataManagementService
from tutopy.services.exceptions import DomainError
from tutopy.ui.dialogs.clear_data_dialog import ClearDataDialog
from tutopy.ui.dialogs.import_conflicts_dialog import ImportConflictsDialog
from tutopy.ui.main_window import MainWindow


class DataManagementController:
    def __init__(self, window: MainWindow, importer: BulkImportService,
                 data_service: DataManagementService, on_changed=None,
                 conflict_dialog=ImportConflictsDialog,
                 clear_dialog=ClearDataDialog):
        self.window = window
        self.importer = importer
        self.data_service = data_service
        self.on_changed = on_changed or (lambda: None)
        self.conflict_dialog = conflict_dialog
        self.clear_dialog = clear_dialog
        view = window.data_tools
        view.template_requested.connect(self.export_template)
        view.import_requested.connect(self.import_spreadsheet)
        view.clear_requested.connect(self.clear_all)

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
            self.window, "Importar dades", "", "Full de càlcul Excel (*.xlsx)"
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
