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


def _stub_message_box(monkeypatch, choice_text):
    """Simula la resposta a un `QMessageBox` de tres botons triant-ne un pel text."""
    monkeypatch.setattr(QMessageBox, "exec", lambda self: 0)

    def clicked_button(self):
        if choice_text is None:
            return None
        return next(
            (button for button in self.buttons() if button.text() == choice_text), None,
        )
    monkeypatch.setattr(QMessageBox, "clickedButton", clicked_button)


def _template_dialog_factory(disposition, parameters, teacher_mode="strip",
                              teacher_position="center", leftover_criterion="back",
                              fill_order="rows", fill_random=False):
    return lambda student_count, other_layouts, defaults, parent: SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        values=lambda: {
            "disposition": disposition, "parameters": parameters,
            "teacher_mode": teacher_mode, "teacher_position": teacher_position,
            "leftover_criterion": leftover_criterion, "fill_order": fill_order,
            "fill_random": fill_random,
        },
    )


def test_apply_template_sense_distribucio_mostra_error(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.apply_template()
    assert env.window.errors == ["Selecciona o crea primer una distribució."]


def test_apply_template_fresh_omple_alfabeticament(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2},
    )
    env.controller.apply_template()
    assert env.controller.grid.rows == 1 and env.controller.grid.columns == 2
    assert len(env.controller.pending) == 0
    # alfabètic per cognoms: Bosch abans que Camps
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)


def test_apply_template_cancel_lar_dialeg_no_canvia_res(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()

    def cancelling_factory(student_count, other_layouts, defaults, parent):
        return SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected, values=lambda: {})
    env.controller.template_dialog_factory = cancelling_factory
    original_grid = env.controller.grid
    env.controller.apply_template()
    assert env.controller.grid is original_grid


def test_apply_template_amb_assignacions_demana_confirmacio(env, monkeypatch):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)

    _stub_message_box(monkeypatch, None)  # "Cancel·lar"
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2},
    )
    original_grid = env.controller.grid
    env.controller.apply_template()
    assert env.controller.grid is original_grid


def test_apply_template_buidar_torna_tothom_a_pendents(env, monkeypatch):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)

    _stub_message_box(monkeypatch, "Buidar")
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 2, "columns": 2},
    )
    env.controller.apply_template()
    assert env.controller.grid.assigned() == {}
    pending_ids = {student.id for student in env.controller.pending}
    assert pending_ids == {env.student_a.id, env.student_b.id}


def test_apply_template_mantenir_ordre_preserva_la_posicio_relativa(env, monkeypatch):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    # B abans que A a la graella (encara que alfabèticament A vagi primer)
    env.controller.move_student(env.student_b.id, "pending", 0, 0)
    env.controller.move_student(env.student_a.id, "pending", 0, 1)

    _stub_message_box(monkeypatch, "Mantenir l'ordre")
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2},
    )
    env.controller.apply_template()
    # l'ordre de lectura anterior (B, A) es conserva a les noves posicions
    assert env.controller.grid.find(env.student_b.id) == (0, 0)
    assert env.controller.grid.find(env.student_a.id) == (0, 1)


def test_apply_template_patro_invalid_mostra_error(env):
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    env.controller.template_dialog_factory = _template_dialog_factory(
        "columns", {"pattern": "invalid", "aisle_width": 1},
    )
    original_grid = env.controller.grid
    env.controller.apply_template()
    assert env.controller.grid is original_grid
    assert env.window.errors
