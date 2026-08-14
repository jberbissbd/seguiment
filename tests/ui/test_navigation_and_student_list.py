from PySide6.QtCore import Qt

from tutopy.application import create_services
from tutopy.controllers.main_controller import MainController
from tutopy.controllers.student_controller import StudentController
from tutopy.database.database import Database
from tutopy.models.messaging import StudentNew
from tutopy.ui.main_window import MainWindow
from tutopy.ui.widgets.sidebar import Sidebar
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.ui.widgets.student_list import StudentList


def test_sidebar_emet_la_seccio_seleccionada(qtbot):
    sidebar = Sidebar()
    qtbot.addWidget(sidebar)

    with qtbot.waitSignal(sidebar.section_changed) as signal:
        qtbot.mouseClick(sidebar.buttons["configuration"], Qt.MouseButton.LeftButton)

    assert signal.args == ["configuration"]
    assert sidebar.buttons["configuration"].isChecked()


def test_student_list_preserva_ids_dels_homonims(qtbot):
    database = Database(":memory:").connect()
    try:
        first = database.students.create(StudentNew("Alex", "Garcia", "2n A"))
        second = database.students.create(StudentNew("Alex", "Garcia", "2n A"))
        widget = StudentList()
        qtbot.addWidget(widget)
        assert not widget.batch_export_button.isEnabled()
        assert widget.create_button.parentWidget() is widget
        assert widget.batch_export_button.parentWidget() is widget
        widget.show()
        qtbot.waitExposed(widget)
        assert widget.create_button.geometry().top() < widget.batch_export_button.geometry().top()
        widget.set_students([first, second])
        assert widget.batch_export_button.isEnabled()

        assert widget.list_widget.count() == 2
        first_item = widget.list_widget.item(0)
        first_widget = widget.list_widget.itemWidget(first_item)
        assert first_item.toolTip() == ""
        assert first_item.sizeHint().height() >= 52
        assert first_widget.minimumHeight() == 52
        assert first_widget.avatar.text() == "AG"
        assert "background-color" in first_widget.avatar.styleSheet()
        first.name = "Àlex"
        widget.set_students([first, second])
        assert widget.list_widget.itemWidget(widget.list_widget.item(0)) is first_widget
        assert first_widget.name.text().startswith("Àlex")
        with qtbot.waitSignal(widget.student_selected) as signal:
            widget.list_widget.setCurrentRow(1)
        assert signal.args == [second.id]
        assert first.uuid != second.uuid
        with qtbot.waitSignal(widget.batch_export_requested):
            qtbot.mouseClick(
                widget.batch_export_button, Qt.MouseButton.LeftButton
            )
    finally:
        database.close()


def test_cerca_coalesceix_pulsacions_consecutives(qtbot):
    widget = StudentList()
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.search_changed, timeout=1_000) as signal:
        widget.search_input.setText("J")
        widget.search_input.setText("Jo")
        widget.search_input.setText("Jordi")

    assert signal.args == ["Jordi"]


def test_main_window_conte_la_navegacio_i_el_detall_de_l_alumne(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert isinstance(window.sidebar, Sidebar)
    assert isinstance(window.student_list, StudentList)
    assert isinstance(window.student_detail, StudentDetailPanel)
    assert window.content_stack.currentWidget() is window._pages["students"]
    assert "configuration" in window._pages
    assert "statistics" in window._pages
    assert "categories" not in window._pages
    assert window.student_detail.tabs.count() == 5


def test_main_controller_carrega_cerca_i_selecciona_alumnes(qtbot, tmp_path):
    database = Database(str(tmp_path / "ui.db")).connect()
    try:
        services = create_services(database)
        jordi = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        services.students.create(StudentNew("Anna", "Serra", "3r B"))
        window = MainWindow()
        qtbot.addWidget(window)
        main_controller = MainController(window)
        controller = StudentController(window, services.students)

        main_controller.start()
        controller.start()
        assert window.student_list.list_widget.count() == 2

        window.student_list.search_input.setText("Jordi")
        qtbot.waitUntil(
            lambda: window.student_list.list_widget.count() == 1,
            timeout=1_000,
        )
        assert window.student_list.list_widget.count() == 1

        window.student_list.list_widget.setCurrentRow(0)
        assert window.student_list.current_student_id() == jordi.id
        assert window.student_detail.student_summary.isVisibleTo(window.student_detail)
        assert window.student_detail.tabs.isVisibleTo(window.student_detail)
    finally:
        database.close()
