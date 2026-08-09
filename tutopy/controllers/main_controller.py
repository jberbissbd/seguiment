from tutopy.application import ServiceContainer
from tutopy.ui.main_window import MainWindow


class MainController:
    """Coordina la navegació i la vista inicial d'alumnes."""

    def __init__(self, window: MainWindow, services: ServiceContainer):
        self.window = window
        self.services = services
        self._connect_signals()

    def start(self) -> None:
        self.show_students()

    def _connect_signals(self) -> None:
        self.window.sidebar.section_changed.connect(self.change_section)
        self.window.student_list.search_changed.connect(self.search_students)
        self.window.student_list.student_selected.connect(self.select_student)
        self.window.student_list.create_requested.connect(self.request_student_creation)

    def change_section(self, section: str) -> None:
        self.window.show_section(section)
        if section == "students":
            self.show_students()

    def show_students(self) -> None:
        students = self.services.students.get_all()
        self.window.student_list.set_students(students)
        self.window.show_status(f"{len(students)} alumnes")

    def search_students(self, query: str) -> None:
        students = self.services.students.search(query)
        self.window.student_list.set_students(students)

    def select_student(self, student_id: int) -> None:
        student = self.services.students.get_by_id(student_id)
        self.window.student_detail.show_student(student)

    def request_student_creation(self) -> None:
        self.window.show_status("La creació d'alumnes s'implementarà a la fase 2.")
