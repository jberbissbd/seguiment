from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton

from tutopy.application import create_services
from tutopy.controllers.main_controller import MainController
from tutopy.controllers.student_controller import StudentController
from tutopy.database.database import Database
from tutopy.models.messaging import Student, StudentNew
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


def test_sidebar_assigna_icones_diferents_a_estadistiques_i_configuracio(qtbot):
    sidebar = Sidebar()
    qtbot.addWidget(sidebar)

    statistics_icon = sidebar.buttons["statistics"].icon()
    configuration_icon = sidebar.buttons["configuration"].icon()
    assert not statistics_icon.isNull()
    assert not configuration_icon.isNull()
    assert Sidebar.SECTIONS[1][2] != Sidebar.SECTIONS[2][2]


def test_student_list_preserva_ids_dels_homonims(qtbot):
    database = Database(":memory:").connect()
    try:
        first = database.students.create(StudentNew("Alex", "Garcia", "2n A"))
        second = database.students.create(StudentNew("Alex", "Garcia", "2n A"))
        widget = StudentList()
        qtbot.addWidget(widget)
        assert not widget.batch_export_button.isEnabled()
        assert not widget.bulk_edit_button.isEnabled()
        assert widget.create_button.parentWidget() is widget
        assert widget.batch_export_button.parentWidget() is widget
        widget.show()
        qtbot.waitExposed(widget)
        assert widget.create_button.geometry().top() < widget.batch_export_button.geometry().top()
        widget.set_students([first, second])
        assert widget.batch_export_button.isEnabled()
        assert widget.bulk_edit_button.isEnabled()

        assert widget.list_widget.model().rowCount() == 2
        view = widget.list_widget
        model = view.model()
        index = model.index(0)
        qtbot.waitUntil(lambda: view.visualRect(index).height() >= 52)
        assert index.data(Qt.ItemDataRole.UserRole) == first.id
        assert index.data(Qt.ItemDataRole.AccessibleTextRole).startswith("Alex Garcia")
        qtbot.mouseMove(view.viewport(), view.visualRect(index).center())
        qtbot.waitUntil(lambda: not view.hover_note_button.isHidden())
        with qtbot.waitSignal(widget.note_create_requested) as note_signal:
            qtbot.mouseClick(view.hover_note_button, Qt.MouseButton.LeftButton)
        assert note_signal.args == [first.id]
        assert widget.current_student_id() == first.id
        assert not view.selected_note_button.isHidden()
        first = replace(first, name="Àlex")
        widget.set_students([first, second])
        assert index.data().startswith("Àlex")
        assert widget.current_student_id() == first.id
        with qtbot.waitSignal(widget.student_selected) as signal:
            view.setFocus()
            qtbot.keyClick(view, Qt.Key.Key_Down)
        assert signal.args == [second.id]
        assert view.selected_note_button.property("student_id") == second.id
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


def test_amplada_minima_preserva_els_botons_de_documents(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.student_detail.show_student(
        Student(1, "uuid", "Maria", "Serra", "4t A")
    )
    window.student_detail.tabs.setCurrentWidget(window.student_detail.document_tab)
    window.show()
    qtbot.waitExposed(window)

    tab = window.student_detail.document_tab
    buttons = (
        tab.actions.create_button,
        tab.open_button,
        tab.export_button,
        tab.actions.edit_button,
        tab.actions.delete_button,
    )
    assert window.minimumWidth() == 1180
    assert all(button.width() >= button.sizeHint().width() for button in buttons)
    assert all(button.minimumWidth() == 0 for button in buttons)


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
        assert window.student_list.list_widget.model().rowCount() == 2

        window.student_list.search_input.setText("Jordi")
        qtbot.waitUntil(
            lambda: window.student_list.list_widget.model().rowCount() == 1,
            timeout=1_000,
        )
        assert window.student_list.list_widget.model().rowCount() == 1

        window.student_list.select_student(jordi.id)
        assert window.student_list.current_student_id() == jordi.id
        assert window.student_detail.student_summary.isVisibleTo(window.student_detail)
        assert window.student_detail.tabs.isVisibleTo(window.student_detail)
    finally:
        database.close()


def test_llista_virtualitzada_preserva_seleccio_i_accions_en_reordenar(qtbot):
    """Les files no creen widgets i la selecció segueix la identitat de l'alumne."""
    widget = StudentList()
    qtbot.addWidget(widget)
    students = [Student(i, str(i), "Nom", str(i), "Grup") for i in range(1000)]
    widget.set_students(students)
    widget.select_student(500)
    widget.set_students(list(reversed(students)))
    assert widget.current_student_id() == 500
    assert len(widget.list_widget.findChildren(QToolButton)) == 2
    index = widget.list_widget.currentIndex()
    assert widget.list_widget.indexWidget(index) is None
    with qtbot.waitSignal(widget.edit_requested) as signal:
        widget.list_widget.doubleClicked.emit(index)
    assert signal.args == [500]
    widget.set_students(students[:10])
    assert widget.current_student_id() is None
    assert not widget.edit_button.isEnabled()
    assert not widget.delete_button.isEnabled()
    assert widget.list_widget.selected_note_button.isHidden()
    widget.set_students([])
    assert not widget.batch_export_button.isEnabled()
    assert not widget.bulk_edit_button.isEnabled()


def test_boto_de_nota_segueix_la_fila_en_desplacar_i_accepta_teclat(qtbot):
    """El botó seleccionat no queda sobre una altra fila en desplaçar la vista."""
    widget = StudentList()
    qtbot.addWidget(widget)
    widget.resize(400, 500)
    widget.set_students([
        Student(i, str(i), "Nom", str(i), "Grup") for i in range(100)
    ])
    widget.show()
    qtbot.waitExposed(widget)
    view = widget.list_widget
    widget.select_student(0)
    qtbot.waitUntil(lambda: not view.selected_note_button.isHidden())
    view.scrollToBottom()
    assert view.selected_note_button.isHidden()
    widget.select_student(99)
    button = view.selected_note_button
    assert not button.isHidden()
    assert view.visualRect(view.currentIndex()).contains(button.geometry().center())
    button.setFocus()
    with qtbot.waitSignal(widget.note_create_requested) as signal:
        qtbot.keyClick(button, Qt.Key.Key_Space)
    assert signal.args == [99]
