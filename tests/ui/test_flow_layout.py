from PySide6.QtCore import QRect
from PySide6.QtWidgets import QLabel, QWidget

from tutopy.ui.widgets.flow_layout import FlowLayout


def test_flow_layout_distribueix_elements_i_calcula_alcada(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    layout = FlowLayout(parent, margin=4, spacing=6)
    labels = [QLabel("Element llarg", parent) for _ in range(3)]
    for label in labels:
        label.setMinimumSize(90, 20)
        layout.addWidget(label)

    one_line = layout.heightForWidth(400)
    wrapped = layout.heightForWidth(120)
    layout.setGeometry(QRect(0, 0, 120, wrapped))

    assert layout.count() == 3
    assert layout.itemAt(-1) is None
    assert layout.itemAt(99) is None
    assert wrapped > one_line
    assert labels[1].geometry().y() > labels[0].geometry().y()
    assert layout.minimumSize().width() >= 98
    assert layout.expandingDirections().value == 0
    assert layout.hasHeightForWidth()
    assert layout.sizeHint() == layout.minimumSize()


def test_flow_layout_extreu_i_elimina_widgets(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    layout = FlowLayout(parent)
    first = QLabel("Primer")
    second = QLabel("Segon")
    layout.addWidget(first)
    layout.addWidget(second)

    assert layout.takeAt(99) is None
    assert layout.takeAt(0).widget() is first
    assert layout.count() == 1
    layout.clear()
    assert layout.count() == 0
