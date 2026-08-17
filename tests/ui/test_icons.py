from PySide6.QtWidgets import QAbstractButton, QDialogButtonBox

from tutopy.ui.dialogs.contact_dialog import ContactDialog
from tutopy.ui.main_window import MainWindow
from tutopy.ui.resources import ACTION_ICONS, application_icon, asset_path
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel


def test_recursos_vectorials_existeixen():
    for filename in (
        "tutopy.svg", "notes.svg", "descriptors.svg", "contacts.svg",
        "documents.svg", "history.svg",
        "students.svg", "categories.svg", "data.svg",
        "export.svg",
    ):
        assert asset_path(filename).is_file()
    assert all(asset_path(filename).is_file() for filename in ACTION_ICONS.values())


def test_icona_de_creacio_contrasta_amb_els_botons_primaris():
    content = asset_path(ACTION_ICONS["add"]).read_text(encoding="utf-8")
    assert 'stroke="#FFFFFF"' in content


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


def test_accions_de_la_finestra_principal_tenen_icones(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    action_buttons = [
        button for button in window.findChildren(QAbstractButton)
        if button.text() and not button.isCheckable()
    ]
    assert action_buttons
    assert all(not button.icon().isNull() for button in action_buttons)


def test_botons_estandard_dels_dialegs_tenen_icones(qtbot):
    dialog = ContactDialog()
    qtbot.addWidget(dialog)
    assert not dialog.buttons.button(
        QDialogButtonBox.StandardButton.Save
    ).icon().isNull()
    assert not dialog.buttons.button(
        QDialogButtonBox.StandardButton.Cancel
    ).icon().isNull()
