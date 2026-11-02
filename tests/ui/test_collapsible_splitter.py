from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from tutopy.ui.widgets.collapsible_splitter import CollapsibleSplitter


def _build_splitter(qtbot):
    splitter = CollapsibleSplitter(Qt.Orientation.Horizontal)
    qtbot.addWidget(splitter)
    first = QLabel("Primer panell")
    second = QLabel("Segon panell")
    first.setMinimumWidth(200)
    splitter.addWidget(first)
    splitter.addWidget(second)
    splitter.resize(400, 200)
    splitter.show()
    return splitter, first


def test_toggle_first_panel_redueix_i_restaura_lamplada(qtbot):
    splitter, first = _build_splitter(qtbot)
    assert first.width() > 0

    splitter.toggle_first_panel()
    assert first.width() == 0

    splitter.toggle_first_panel()
    assert first.width() > 0


def test_el_manec_es_manté_visible_quan_es_plega(qtbot):
    """Regressió: Qt amaga el mànec d'un panell ocult amb `setVisible(False)`;
    per això `toggle_first_panel` l'ha de reduir a zero sense amagar-lo."""
    splitter, _first = _build_splitter(qtbot)
    handle = splitter.handle(1)
    assert handle.isHidden() is False

    splitter.toggle_first_panel()
    assert handle.isHidden() is False

    splitter.toggle_first_panel()
    assert handle.isHidden() is False


def test_clic_al_boto_del_manec_commuta_el_primer_panell(qtbot):
    splitter, first = _build_splitter(qtbot)
    handle = splitter.handle(1)
    toggle_center = handle._toggle_rect().center()

    qtbot.mouseClick(handle, Qt.MouseButton.LeftButton, pos=toggle_center)
    assert first.width() == 0

    qtbot.mouseClick(handle, Qt.MouseButton.LeftButton, pos=toggle_center)
    assert first.width() > 0


def test_arrossegar_fora_del_boto_no_commuta_el_panell(qtbot):
    splitter, first = _build_splitter(qtbot)
    handle = splitter.handle(1)
    # un punt lluny del botó central, dins del mànec
    far_point = handle._toggle_rect().center()
    far_point.setY(2)

    qtbot.mouseClick(handle, Qt.MouseButton.LeftButton, pos=far_point)
    assert first.width() > 0
