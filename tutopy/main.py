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
from tutopy.database.database import Database
from tutopy.services.directories import get_db_path
from tutopy.ui.main_window import MainWindow


def main() -> int:
    """Punt d'entrada i arrel de composició de l'aplicació."""
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
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

    data_controller = DataManagementController(
        window, services.bulk_import, services.data_management,
        on_changed=refresh_after_data_change,
    )
    main_controller.start()
    student_controller.start()
    note_controller.start()
    category_controller.start()
    app.aboutToQuit.connect(database.close)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
