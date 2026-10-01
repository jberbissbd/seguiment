from PySide6.QtWidgets import QDialogButtonBox, QScrollArea

from tutopy.ui.dialogs.clear_data_dialog import ClearDataDialog
from tutopy.ui.main_window import MainWindow


def test_confirmacio_exigeix_paraula_exacta(qtbot):
    dialog = ClearDataDialog()
    qtbot.addWidget(dialog)
    assert not dialog.ok_button.isEnabled()
    dialog.confirmation_input.setText("eliminar")
    assert not dialog.ok_button.isEnabled()
    dialog.confirmation_input.setText("ELIMINAR")
    assert dialog.ok_button.isEnabled()


def test_finestra_inclou_gestio_de_dades(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert "data" in window.sidebar.buttons
    window.show_section("data")
    assert window.content_stack.currentWidget() is window._pages["data"]
    assert isinstance(window.data_tools_scroll, QScrollArea)
    assert window.data_tools_scroll.widget() is window.data_tools
    assert window.data_tools.report_panel.parentWidget() is not window.data_tools
    assert window.configuration_scroll.widget().isAncestorOf(window.data_tools.report_panel)
    assert window.data_tools.preferences_panel.parentWidget() is not window.data_tools
    assert window.configuration_scroll.widget().isAncestorOf(
        window.data_tools.preferences_panel
    )


def test_casella_de_comprovacio_de_versio_emet_senyal(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    received = []
    window.data_tools.update_check_toggled.connect(received.append)

    window.data_tools.update_check_checkbox.setChecked(True)

    assert received == [True]


def test_set_update_check_enabled_no_reemet_el_senyal(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.data_tools.set_update_check_enabled(True)
    received = []
    window.data_tools.update_check_toggled.connect(received.append)

    window.data_tools.set_update_check_enabled(False)

    assert received == []
    assert window.data_tools.update_check_checkbox.isChecked() is False
