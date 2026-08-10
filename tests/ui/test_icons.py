from tutopy.ui.main_window import MainWindow
from tutopy.ui.resources import application_icon, asset_path
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel


def test_recursos_vectorials_existeixen():
    for filename in (
        "tutopy.svg", "notes.svg", "descriptors.svg", "contacts.svg",
        "documents.svg", "history.svg",
        "students.svg", "categories.svg", "data.svg",
    ):
        assert asset_path(filename).is_file()


def test_pestanyes_tenen_icones(qtbot):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    assert panel.tabs.count() == len(panel.TAB_NAMES)
    assert all(not panel.tabs.tabIcon(index).isNull()
               for index in range(panel.tabs.count()))


def test_finestra_te_icona(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert not application_icon().isNull()
    assert not window.windowIcon().isNull()


def test_seccions_laterals_tenen_icones(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert all(not button.icon().isNull()
               for button in window.sidebar.buttons.values())
