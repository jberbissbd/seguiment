import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from tutopy.application import create_services
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
    window = MainWindow(services)
    app.aboutToQuit.connect(database.close)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
