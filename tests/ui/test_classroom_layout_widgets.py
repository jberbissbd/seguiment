from PySide6.QtGui import QColor, QPixmap

from tutopy.models.classroom_layout import CellType, LayoutGrid
from tutopy.models.messaging import Student
from tutopy.ui.widgets import classroom_layout_mime as mime
from tutopy.ui.widgets.classroom_layout_cell_widget import ClassroomCellWidget
from tutopy.ui.widgets.classroom_layout_grid_widget import ClassroomLayoutGridWidget
from tutopy.ui.widgets.classroom_layout_pending_list import PendingStudentsList

# `_handle_drop` es testeja directament amb un QMimeData, sense construir un
# QDropEvent: cridar `QDropEvent.acceptProposedAction()` fora d'una sessió
# real d'arrossegament de Qt provoca una violació de segment coneguda de
# PySide6, no una excepció Python capturable.


def _write_jpg(tmp_path, name="foto.jpg"):
    path = tmp_path / name
    pixmap = QPixmap(10, 10)
    pixmap.fill(QColor("green"))
    pixmap.save(str(path), "JPG")
    return path


def test_cell_widget_drop_des_de_pendents_emet_move_requested(qtbot):
    cell = ClassroomCellWidget(2, 3)
    qtbot.addWidget(cell)
    with qtbot.waitSignal(cell.move_requested) as signal:
        accepted = cell._handle_drop(mime.encode(7, mime.PENDING_ORIGIN))
    assert accepted is True
    assert signal.args == [7, "pending", 2, 3]


def test_cell_widget_drop_des_d_una_altra_cel_la(qtbot):
    cell = ClassroomCellWidget(0, 0)
    qtbot.addWidget(cell)
    with qtbot.waitSignal(cell.move_requested) as signal:
        cell._handle_drop(mime.encode(9, mime.cell_origin(1, 2)))
    assert signal.args == [9, "cell:1:2", 0, 0]


def test_cell_widget_drop_sobre_cel_la_no_seient_no_emet_res(qtbot):
    cell = ClassroomCellWidget(0, 0)
    qtbot.addWidget(cell)
    cell.update_cell(CellType.AISLE, None, None, False)
    received = []
    cell.move_requested.connect(lambda *args: received.append(args))
    accepted = cell._handle_drop(mime.encode(1, mime.PENDING_ORIGIN))
    assert accepted is False
    assert received == []


def test_cell_widget_return_to_pending_nomes_amb_alumne(qtbot):
    cell = ClassroomCellWidget(0, 0)
    qtbot.addWidget(cell)
    student = Student(5, "uuid", "Maria", "Serra", "4t A")
    cell.update_cell(CellType.SEAT, student, None, False)
    assert cell._student is student


def test_pending_list_drop_des_d_una_cel_la_emet_move_requested(qtbot):
    pending_list = PendingStudentsList()
    qtbot.addWidget(pending_list)
    with qtbot.waitSignal(pending_list.move_requested) as signal:
        accepted = pending_list._handle_drop(mime.encode(3, mime.cell_origin(0, 1)))
    assert accepted is True
    assert signal.args == [3, "cell:0:1"]


def test_pending_list_drop_des_de_pendents_no_emet_res(qtbot):
    pending_list = PendingStudentsList()
    qtbot.addWidget(pending_list)
    received = []
    pending_list.move_requested.connect(lambda *args: received.append(args))
    accepted = pending_list._handle_drop(mime.encode(3, mime.PENDING_ORIGIN))
    assert accepted is True  # s'accepta el drop, però no s'emet res (ja era a pendents)
    assert received == []


def test_pending_list_set_students_mostra_fotos_quan_cal(qtbot, tmp_path):
    pending_list = PendingStudentsList()
    qtbot.addWidget(pending_list)
    student = Student(1, "uuid", "Maria", "Serra", "4t A")
    photo_path = str(_write_jpg(tmp_path))
    pending_list.set_students([student], True, {1: photo_path})
    item = pending_list.item(0)
    assert item.text() == "Maria Serra"
    assert not item.icon().isNull()


def test_grid_widget_inverteix_la_fila_perque_el_professor_quedi_a_baix(qtbot):
    grid_widget = ClassroomLayoutGridWidget()
    qtbot.addWidget(grid_widget)
    grid = LayoutGrid(3, 2)
    grid_widget.rebuild(grid, {}, False, {})
    layout = grid_widget._layout
    # fila de model 0 (davant) ha d'acabar a la fila de pantalla 2 (la darrera)
    cell_front = grid_widget._cells[(0, 0)]
    cell_back = grid_widget._cells[(2, 0)]
    front_index = layout.indexOf(cell_front)
    back_index = layout.indexOf(cell_back)
    front_row, _col, _rs, _cs = layout.getItemPosition(front_index)
    back_row, _col2, _rs2, _cs2 = layout.getItemPosition(back_index)
    assert front_row == 2
    assert back_row == 0


def test_grid_widget_rebuild_mostra_alumnes_assignats(qtbot):
    grid_widget = ClassroomLayoutGridWidget()
    qtbot.addWidget(grid_widget)
    grid = LayoutGrid(2, 2)
    student = Student(1, "uuid", "Maria", "Serra", "4t A")
    grid.assign(1, 0, 0)
    grid_widget.rebuild(grid, {1: student}, False, {})
    cell = grid_widget._cells[(0, 0)]
    assert cell.avatar_label.text() == "MS"


def test_grid_widget_rebuild_mostra_foto_quan_show_photos(qtbot, tmp_path):
    grid_widget = ClassroomLayoutGridWidget()
    qtbot.addWidget(grid_widget)
    grid = LayoutGrid(1, 1)
    student = Student(1, "uuid", "Maria", "Serra", "4t A")
    grid.assign(1, 0, 0)
    photo_path = str(_write_jpg(tmp_path))
    grid_widget.rebuild(grid, {1: student}, True, {1: photo_path})
    cell = grid_widget._cells[(0, 0)]
    assert cell.avatar_label.text() == ""
    assert not cell.avatar_label.pixmap().isNull()
