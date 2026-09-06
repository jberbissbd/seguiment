"""Punt d'entrada de l'aplicació.

Crea els serveis, els controladors i la finestra principal, i arrenca el
bucle d'esdeveniments de Qt.
"""

import sys
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from tutopy.application import ServiceContainer, create_services
from tutopy.controllers.main_controller import MainController
from tutopy.controllers.student_controller import StudentController
from tutopy.controllers.note_controller import NoteController
from tutopy.controllers.catalog_controller import CategoryController
from tutopy.controllers.student_related_controller import StudentRelatedController
from tutopy.controllers.data_management_controller import DataManagementController
from tutopy.controllers.report_controller import ReportController
from tutopy.controllers.statistics_controller import StatisticsController
from tutopy.database.database import Database
from tutopy.services.directories import get_db_path
from tutopy.services.desktop_integration import DESKTOP_ID, install_desktop_entry
from tutopy.ui.main_window import MainWindow
from tutopy.ui.resources import application_icon, asset_path


@dataclass(frozen=True, slots=True)
class ControllerContainer:
    """Controladors de la UI, conservats mentre l'aplicació està activa."""

    main: MainController
    students: StudentController
    notes: NoteController
    categories: CategoryController
    student_related: StudentRelatedController
    data_management: DataManagementController
    reports: ReportController
    statistics: StatisticsController

    def start(self) -> None:
        """Carrega només els controladors que tenen estat inicial visible.

        Les estadístiques no es carreguen aquí: `StatisticsController` ja
        escolta el canvi de secció de la barra lateral i es carrega sol la
        primera vegada que l'usuari hi navega, evitant consultes a la base
        de dades a l'arrencada per a una pestanya que potser no s'obrirà mai
        en aquella sessió.
        """
        for controller in (
            self.main,
            self.students,
            self.notes,
            self.categories,
            self.reports,
        ):
            controller.start()


def create_controllers(
    window: MainWindow,
    services: ServiceContainer,
) -> ControllerContainer:
    """Connecta controladors, serveis i callbacks de refresc de la UI."""
    main_controller = MainController(window)
    student_controller = StudentController(window, services.students)
    note_controller = NoteController(
        window,
        services.notes,
        services.categories,
        services.academic_courses,
    )
    related_controller = StudentRelatedController(
        window,
        services.students,
        services.annotations,
        services.contacts,
        services.documents,
        services.academic_courses,
    )

    def refresh_notes() -> None:
        note_controller.refresh_options()
        note_controller.refresh()

    category_controller = CategoryController(
        window,
        services.categories,
        on_changed=refresh_notes,
    )
    report_controller = ReportController(
        window,
        services.students,
        services.academic_courses,
        services.report_configuration,
        services.report_files,
        services.student_exports,
    )

    def refresh_after_data_change() -> None:
        window.student_detail.clear()
        student_controller.refresh()
        category_controller.refresh()
        refresh_notes()
        report_controller.refresh()

    data_controller = DataManagementController(
        window,
        services.bulk_import,
        services.data_management,
        services.transfers,
        services.students,
        on_changed=refresh_after_data_change,
    )
    statistics_controller = StatisticsController(
        window,
        services.statistics,
        services.students,
        services.academic_courses,
        services.categories,
    )
    return ControllerContainer(
        main=main_controller,
        students=student_controller,
        notes=note_controller,
        categories=category_controller,
        student_related=related_controller,
        data_management=data_controller,
        reports=report_controller,
        statistics=statistics_controller,
    )


def main() -> int:
    """Punt d'entrada i arrel de composició de l'aplicació."""
    if sys.argv[1:] == ["--install-desktop"]:
        return _install_desktop()
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Tutopy")
    app.setDesktopFileName(DESKTOP_ID)
    app.setWindowIcon(application_icon())
    database = Database(str(get_db_path())).connect()
    services = create_services(database)
    window = MainWindow()
    controllers = create_controllers(window, services)
    # Conserva els controladors durant tot el bucle d'esdeveniments de Qt.
    window.controllers = controllers
    controllers.start()
    app.aboutToQuit.connect(database.close)
    window.show()
    return app.exec()


def _install_desktop() -> int:
    if sys.platform != "linux":
        print("La instal·lació del llançador només està disponible a Linux.", file=sys.stderr)
        return 1
    command = [sys.executable]
    if not getattr(sys, "frozen", False):
        command.extend(["-m", "tutopy.main"])
    try:
        path = install_desktop_entry(command, asset_path("tutopy.svg"))
    except (OSError, ValueError) as error:
        print(f"No s'ha pogut instal·lar el llançador: {error}", file=sys.stderr)
        return 1
    print(f"Llançador instal·lat: {path}\nJa pots obrir Tutopy des del menú d'aplicacions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
