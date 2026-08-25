"""Controlador de la vista d'estadístiques.

Connecta els filtres de la vista amb el servei d'estadístiques i en
construeix l'instantani (snapshot) que es mostra a l'usuari.
"""

from tutopy.models.statistics import StatisticsFilters
from tutopy.services.exceptions import DomainError
from tutopy.ui.main_window import MainWindow


class StatisticsController:
    """Gestiona el filtratge i la visualització de l'instantani estadístic."""

    def __init__(self, window: MainWindow, statistics, students, courses,
                 categories, error_handler=None):
        """Desa les dependències i connecta la petició d'actualització de la vista."""
        self.window = window
        self.statistics = statistics
        self.students = students
        self.courses = courses
        self.categories = categories
        self.error_handler = error_handler or window.show_error
        self.view = window.statistics_view
        self.view.refresh_requested.connect(self.refresh)
        window.sidebar.section_changed.connect(self._section_changed)

    def start(self) -> None:
        """Carrega les opcions de filtre disponibles a la vista."""
        self.refresh_options()

    def refresh_options(self) -> None:
        """Actualitza els cursos, grups i categories disponibles als filtres."""
        self.view.set_filter_options(
            self.statistics.get_available_courses(), self.students.get_groups(),
            self.categories.get_all(),
        )

    def refresh(self) -> None:
        """Recalcula l'instantani estadístic segons els filtres de la vista."""
        self.refresh_options()
        values = self.view.filter_values()
        try:
            snapshot = self.statistics.get_snapshot(StatisticsFilters(**values))
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.view.set_snapshot(snapshot, self._context(values, snapshot.student_count))
        self.window.show_status("Estadístiques actualitzades")

    def _section_changed(self, section: str) -> None:
        if section == "statistics":
            self.refresh()

    def _context(self, values, student_count):
        parts = [f"{student_count} alumnes inclosos"]
        if values["group_name"]:
            parts.append(f"grup {values['group_name']}")
        if values["date_from"]:
            parts.append(f"del {self._display_date(values['date_from'])} "
                         f"al {self._display_date(values['date_to'])}")
        return " · ".join(parts)

    @staticmethod
    def _display_date(value: str) -> str:
        year, month, day = value.split("-")
        return f"{day}/{month}/{year}"
