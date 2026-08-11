import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from tutopy.application import create_services
from tutopy.controllers.main_controller import MainController
from tutopy.controllers.student_controller import StudentController
from tutopy.controllers.note_controller import NoteController
from tutopy.controllers.catalog_controller import CategoryController
from tutopy.controllers.student_related_controller import StudentRelatedController
from tutopy.controllers.data_management_controller import DataManagementController
from tutopy.controllers.report_controller import ReportController
from tutopy.database.database import Database
from tutopy.services.directories import get_db_path
from tutopy.ui.main_window import MainWindow
from tutopy.ui.resources import application_icon


def main() -> int:
    """Punt d'entrada i arrel de composició de l'aplicació."""
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Tutopy")
    app.setWindowIcon(application_icon())
    database = Database(str(get_db_path())).connect()
    services = create_services(database)
    window = MainWindow()
    main_controller = MainController(window)
    student_controller = StudentController(window, services.students)
    note_controller = NoteController(
        window,
        services.notes,
        services.categories,
        services.academic_courses,
    )
    related_controller = StudentRelatedController(
        window, services.students, services.annotations, services.contacts,
        services.documents, services.academic_courses,
    )

    def refresh_note_catalogs():
        note_controller.refresh_options()
        note_controller.refresh()

    category_controller = CategoryController(
        window, services.categories, on_changed=refresh_note_catalogs
    )

    def refresh_after_data_change():
        window.student_detail.clear()
        student_controller.refresh()
        category_controller.refresh()
        note_controller.refresh_options()
        note_controller.refresh()
        report_controller.refresh()

    data_controller = DataManagementController(
        window, services.bulk_import, services.data_management,
        on_changed=refresh_after_data_change,
    )
    report_controller = ReportController(
        window, services.students, services.academic_courses,
        services.report_configuration, services.spreadsheet_reports,
        services.word_reports,
    )
    # Conserva els controladors durant tot el bucle d'esdeveniments de Qt.
    window.controllers = (
        main_controller, student_controller, note_controller, category_controller,
        related_controller, data_controller, report_controller,
    )
    main_controller.start()
    student_controller.start()
    note_controller.start()
    category_controller.start()
    report_controller.start()
    app.aboutToQuit.connect(database.close)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
