import pytest

from tutopy.application import create_services
from tutopy.controllers.main_controller import MainController
from tutopy.controllers.statistics_controller import StatisticsController
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.ui.main_window import MainWindow
from tutopy.database.database import Database


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "statistics-controller.db")).connect()
    yield database
    database.close()


def test_obrir_estadistiques_actualitza_filtres_i_resultats(db, qtbot):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Seguiment"
    ))
    window = MainWindow()
    qtbot.addWidget(window)
    navigation = MainController(window)
    controller = StatisticsController(
        window, services.statistics, services.students,
        services.academic_courses, services.categories,
    )
    navigation.start()
    controller.start()

    window.sidebar.section_changed.emit("statistics")

    assert window.statistics_view.summary_values["notes"].text() == "1"
    assert window.statistics_view.group_input.findText("4t A") >= 0
    assert window.content_stack.currentWidget() is window._pages["statistics"]


def test_actualitzar_mante_filtres_seleccionats(db, qtbot):
    services = create_services(db)
    services.students.create(StudentNew("Laia", "Martí", "4t A"))
    window = MainWindow()
    qtbot.addWidget(window)
    controller = StatisticsController(
        window, services.statistics, services.students,
        services.academic_courses, services.categories,
    )
    controller.start()
    view = window.statistics_view
    view.group_input.setCurrentIndex(view.group_input.findText("4t A"))

    controller.refresh()

    assert view.group_input.currentData() == "4t A"
    assert "1 alumnes inclosos" in view.context_label.text()


def test_selector_no_mostra_cursos_sense_notes(db, qtbot):
    services = create_services(db)
    student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.academic_courses.get_or_create("2025-2026")
    services.notes.create(NoteNew(
        student.id, category.id, "2026-09-10", 0, "Curs nou"
    ))
    window = MainWindow()
    qtbot.addWidget(window)
    controller = StatisticsController(
        window, services.statistics, services.students,
        services.academic_courses, services.categories,
    )

    controller.start()

    choices = [
        window.statistics_view.course_input.itemText(index)
        for index in range(window.statistics_view.course_input.count())
    ]
    assert "2026-2027" in choices
    assert "2025-2026" not in choices


def test_canvi_de_filtre_refresca_les_estadistiques(db, qtbot):
    services = create_services(db)
    first = services.students.create(StudentNew("Laia", "Martí", "4t A"))
    second = services.students.create(StudentNew("Pau", "Puig", "4t B"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(first.id, category.id, "2026-02-01", 0, "A"))
    services.notes.create(NoteNew(second.id, category.id, "2026-02-02", 0, "B"))
    services.notes.create(NoteNew(second.id, category.id, "2026-02-03", 0, "C"))
    window = MainWindow()
    qtbot.addWidget(window)
    controller = StatisticsController(
        window, services.statistics, services.students,
        services.academic_courses, services.categories,
    )
    controller.start()
    controller.refresh()
    view = window.statistics_view

    view.group_input.setCurrentIndex(view.group_input.findData("4t B"))
    qtbot.waitUntil(
        lambda: view.summary_values["notes"].text() == "2", timeout=1_000
    )

    assert view.filter_values()["group_name"] == "4t B"
