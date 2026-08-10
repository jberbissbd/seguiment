from PySide6.QtWidgets import QDialogButtonBox

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
