from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDialog, QMessageBox

from tutopy.application import create_services
from tutopy.controllers.classroom_layout_controller import ClassroomLayoutController
from tutopy.database.database import Database
from tutopy.models.messaging import StudentNew
from tutopy.ui.main_window import MainWindow


@pytest.fixture
def env(qtbot, tmp_path):
    database = Database(str(tmp_path / "classroom.db")).connect()
    services = create_services(database)
    window = MainWindow()
    qtbot.addWidget(window)
    window.errors = []
    window.show_error = window.errors.append
    student_a = services.students.create(StudentNew("Anna", "Bosch", "1r A"))
    student_b = services.students.create(StudentNew("Bet", "Camps", "1r A"))
    controller = ClassroomLayoutController(
        window, services.classroom_layouts, services.students,
        dialog_factory=lambda group_name, parent: SimpleNamespace(
            exec=lambda: QDialog.DialogCode.Accepted,
            values=lambda: {
                "group_name": group_name, "name": "Nova", "rows": 3, "columns": 3,
                "teacher_mode": "strip", "teacher_position": "center",
            },
        ),
    )
    env = SimpleNamespace(
        database=database, services=services, window=window, controller=controller,
        student_a=student_a, student_b=student_b,
    )
    yield env
    database.close()


def test_section_changed_carrega_grups_i_primer_grup(env):
    env.window.sidebar.section_changed.emit("classroom")
    assert env.controller.group_name == "1r A"


def test_section_changed_nomes_carrega_un_cop(env, monkeypatch):
    env.window.sidebar.section_changed.emit("classroom")
    calls = []
    monkeypatch.setattr(env.controller, "select_group", lambda *a: calls.append(a))
    env.window.sidebar.section_changed.emit("classroom")
    assert calls == []


def test_new_layout_el_selecciona(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    assert env.controller.layout is not None
    assert env.controller.layout.name == "Nova"
    assert env.controller.grid.rows == 3


def test_move_student_des_de_pendents_intercanvia_i_desplaca(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)
    assert env.controller.pending == []

    env.controller.move_student(env.student_a.id, "cell:0:1", 0, 0)
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)
    assert env.controller.dirty is True


def test_return_to_pending(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.return_to_pending(env.student_a.id)
    assert env.controller.grid.find(env.student_a.id) is None
    assert any(student.id == env.student_a.id for student in env.controller.pending)


def test_save_neteja_el_dirty_i_persisteix(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    assert env.controller.dirty is True
    env.controller.save()
    assert env.controller.dirty is False

    _, grid, _ = env.services.classroom_layouts.load(env.controller.layout.id)
    assert grid.find(env.student_a.id) == (0, 0)


def test_set_active_marca_la_distribucio(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.set_active()
    active = env.services.classroom_layouts.get_active("1r A")
    assert active.id == env.controller.layout.id


def test_canvi_de_grup_amb_canvis_sense_desar_demana_confirmacio(env, monkeypatch):
    env.services.students.create(StudentNew("Clara", "Diaz", "1r B"))
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    assert env.controller.dirty is True

    monkeypatch.setattr(
        QMessageBox, "exec", lambda self: QMessageBox.StandardButton.NoButton
    )
    clicked = Mock()
    monkeypatch.setattr(QMessageBox, "clickedButton", lambda self: clicked)
    # Simulem "Cancel·lar": cap botó Desar/Descartar coincideix amb `clicked`.
    layout_before = env.controller.layout
    env.controller.select_group("1r B")
    assert env.controller.layout is layout_before
    assert env.controller.dirty is True


def test_resize_torna_a_pendents_els_desplacats(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 2, 2)
    env.controller.resize(2, 2)
    assert env.controller.grid.rows == 2 and env.controller.grid.columns == 2
    assert any(student.id == env.student_a.id for student in env.controller.pending)


def test_place_teacher_canvia_el_mode_i_desplaca_alumnes(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.place_teacher(0, 0)
    assert env.controller.teacher_mode == "grid"
    assert any(student.id == env.student_a.id for student in env.controller.pending)
    assert env.controller.grid.cells[(0, 0)].cell_type.value == "teacher"
