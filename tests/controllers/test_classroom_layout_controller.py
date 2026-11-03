"""Tests del controlador de distribució d'aula."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from tutopy.application import create_services
from tutopy.controllers.classroom_layout_controller import ClassroomLayoutController
from tutopy.database.database import Database
from tutopy.models.classroom_layout import ClassroomLayoutNew
from tutopy.models.messaging import StudentNew
from tutopy.ui.main_window import MainWindow

NO_LAYOUT_SELECTED_ERROR = "Selecciona o crea primer una distribució."

NEW_LAYOUT_VALUES = {
    "name": "Nova", "disposition": "free", "parameters": {"rows": 3, "columns": 3},
    "teacher_mode": "strip", "teacher_position": "center",
    "leftover_criterion": "back", "fill_order": "rows", "fill_direction": "left",
    "fill_random": False,
}


def _new_layout_dialog_factory(group_name, student_count, other_layouts, defaults, parent):
    return SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        values=lambda: dict(NEW_LAYOUT_VALUES, group_name=group_name),
    )


@pytest.fixture
def env(qtbot, tmp_path):
    """Construeix la finestra, els serveis i el controlador de distribució d'aula."""
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
        dialog_factory=_new_layout_dialog_factory,
    )
    env = SimpleNamespace(
        database=database, services=services, window=window, controller=controller,
        student_a=student_a, student_b=student_b,
    )
    yield env
    database.close()


def _blank_layout(env, rows=3, columns=3):
    """Crea i selecciona una distribució buida, sense passar pel diàleg.

    Útil per als tests que només volen comprovar la mecànica de la
    graella (arrossegar, redimensionar, desar...) sense que l'ompliment
    automàtic de `new_layout()` ja hi col·loqui els alumnes.
    """
    layout = env.services.classroom_layouts.create_layout(
        ClassroomLayoutNew(env.controller.group_name, "Nova", rows, columns)
    )
    env.controller.select_layout(layout.id)
    return layout


def test_section_changed_carrega_grups_i_primer_grup(env):
    """Section changed càrrega grups i primer grup."""
    env.window.sidebar.section_changed.emit("classroom")
    assert env.controller.group_name == "1r A"


def test_section_changed_nomes_carrega_un_cop(env, monkeypatch):
    """Section changed només càrrega un cop."""
    env.window.sidebar.section_changed.emit("classroom")
    calls = []
    monkeypatch.setattr(env.controller, "select_group", lambda *a: calls.append(a))
    env.window.sidebar.section_changed.emit("classroom")
    assert calls == []


def test_new_layout_el_selecciona(env):
    """New layout el selecciona."""
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    assert env.controller.layout is not None
    assert env.controller.layout.name == "Nova"
    assert env.controller.grid.rows == 3


def test_new_layout_omple_directament_amb_les_opcions_triades(env):
    """La distribució ja surt amb la forma i l'ompliment del diàleg, no en blanc."""
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.new_layout()
    assert env.controller.pending == []
    # alfabètic per cognoms: Bosch abans que Camps
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)
    assert env.controller.dirty is True


def test_new_layout_sense_grup_mostra_error(env):
    """New layout sense grup mostra error."""
    env.controller.new_layout()
    assert env.window.errors == ["Selecciona primer un grup."]


def test_move_student_des_de_pendents_intercanvia_i_desplaca(env):
    """Move student des de pendents intercanvia i desplaca."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)
    assert env.controller.pending == []

    env.controller.move_student(env.student_a.id, "cell:0:1", 0, 0)
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)
    assert env.controller.dirty is True


def test_return_to_pending(env):
    """Return to pending."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.return_to_pending(env.student_a.id)
    assert env.controller.grid.find(env.student_a.id) is None
    assert any(student.id == env.student_a.id for student in env.controller.pending)


def test_save_neteja_el_dirty_i_persisteix(env):
    """Save neteja el dirty i persisteix."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    assert env.controller.dirty is True
    env.controller.save()
    assert env.controller.dirty is False

    _, grid, _ = env.services.classroom_layouts.load(env.controller.layout.id)
    assert grid.find(env.student_a.id) == (0, 0)


def test_set_active_marca_la_distribucio(env):
    """Set active marca la distribució."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.set_active()
    active = env.services.classroom_layouts.get_active("1r A")
    assert active.id == env.controller.layout.id


def test_canvi_de_grup_amb_canvis_sense_desar_demana_confirmacio(env, monkeypatch):
    """Canvi de grup amb canvis sense desar demana confirmació."""
    env.services.students.create(StudentNew("Clara", "Diaz", "1r B"))
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
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
    """Resize torna a pendents els desplacats."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 2, 2)
    env.controller.resize(2, 2)
    assert env.controller.grid.rows == 2
    assert env.controller.grid.columns == 2
    assert any(student.id == env.student_a.id for student in env.controller.pending)


def test_place_teacher_canvia_el_mode_i_desplaca_alumnes(env):
    """Place teacher canvia el mode i desplaca alumnes."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.place_teacher(0, 0)
    assert env.controller.teacher_mode == "grid"
    assert any(student.id == env.student_a.id for student in env.controller.pending)
    assert env.controller.grid.cells[(0, 0)].cell_type.value == "teacher"


def _template_dialog_factory(disposition, parameters, teacher_mode="strip",
                              teacher_position="center", leftover_criterion="back",
                              fill_order="rows", fill_random=False, fill_direction="left"):
    return lambda student_count, other_layouts, defaults, parent: SimpleNamespace(
        exec=lambda: QDialog.DialogCode.Accepted,
        values=lambda: {
            "disposition": disposition, "parameters": parameters,
            "teacher_mode": teacher_mode, "teacher_position": teacher_position,
            "leftover_criterion": leftover_criterion, "fill_order": fill_order,
            "fill_random": fill_random, "fill_direction": fill_direction,
        },
    )


def test_apply_template_sense_distribucio_mostra_error(env):
    """Apply template sense distribució mostra error."""
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.apply_template()
    assert env.window.errors == [NO_LAYOUT_SELECTED_ERROR]


def test_apply_template_fresh_omple_alfabeticament(env):
    """Apply template fresh omple alfabèticament."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2},
    )
    env.controller.apply_template()
    assert env.controller.grid.rows == 1
    assert env.controller.grid.columns == 2
    assert len(env.controller.pending) == 0
    # alfabètic per cognoms: Bosch abans que Camps
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)


def test_apply_template_cancel_lar_dialeg_no_canvia_res(env):
    """Apply template cancel·lar diàleg no canvia res."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)

    def cancelling_factory(student_count, other_layouts, defaults, parent):
        return SimpleNamespace(exec=lambda: QDialog.DialogCode.Rejected, values=lambda: {})
    env.controller.template_dialog_factory = cancelling_factory
    original_grid = env.controller.grid
    env.controller.apply_template()
    assert env.controller.grid is original_grid


def test_apply_template_amb_assignacions_no_demana_res_i_laplica_directament(env, monkeypatch):
    """Aplicar una plantilla sobre una distribució ja ocupada no demana res: la refà."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    # B abans que A a la graella (encara que alfabèticament A vagi primer)
    env.controller.move_student(env.student_b.id, "pending", 0, 0)
    env.controller.move_student(env.student_a.id, "pending", 0, 1)

    def exec_fails(self):
        raise AssertionError("apply_template no hauria de mostrar cap QMessageBox")
    monkeypatch.setattr(QMessageBox, "exec", exec_fails)

    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2},
    )
    env.controller.apply_template()
    # alfabètic per cognoms (Bosch, Camps), independent de l'ordre anterior
    assert env.controller.grid.find(env.student_a.id) == (0, 0)
    assert env.controller.grid.find(env.student_b.id) == (0, 1)


def test_clear_layout_buida_tots_els_assignats(env):
    """Clear layout buida tots els assignats."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)

    env.controller.clear_layout()
    assert env.controller.grid.assigned() == {}
    pending_ids = {student.id for student in env.controller.pending}
    assert pending_ids == {env.student_a.id, env.student_b.id}
    assert env.controller.dirty is True


def test_clear_layout_sense_distribucio_mostra_error(env):
    """Clear layout sense distribució mostra error."""
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.clear_layout()
    assert env.window.errors == [NO_LAYOUT_SELECTED_ERROR]


def test_apply_template_omple_per_columnes_amb_direccio(env):
    """Apply template omple per columnes amb direcció."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.template_dialog_factory = _template_dialog_factory(
        "free", {"rows": 1, "columns": 2}, fill_order="columns", fill_direction="right",
    )
    env.controller.apply_template()
    # alfabètic per cognoms (Bosch, Camps): amb els dos seients ocupats, "des de la
    # dreta" fa que el primer (Bosch) vagi a la columna més alta.
    assert env.controller.grid.find(env.student_a.id) == (0, 1)
    assert env.controller.grid.find(env.student_b.id) == (0, 0)


def test_pendents_es_mantenen_ordenats_per_cognom_despres_de_moviments(env):
    """Pendents es mantenen ordenats per cognom despres de moviments."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.move_student(env.student_b.id, "pending", 0, 1)
    assert env.controller.pending == []

    # Els tornem a pendents en ordre invers al cognom (Camps abans que Bosch)
    env.controller.return_to_pending(env.student_b.id)
    env.controller.return_to_pending(env.student_a.id)
    assert [student.id for student in env.controller.pending] == [
        env.student_a.id, env.student_b.id,
    ]


def test_apply_template_patro_invalid_mostra_error(env):
    """Apply template patró invàlid mostra error."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.template_dialog_factory = _template_dialog_factory(
        "columns", {"pattern": "invalid", "aisle_width": 1},
    )
    original_grid = env.controller.grid
    env.controller.apply_template()
    assert env.controller.grid is original_grid
    assert env.window.errors


def test_export_layout_sense_distribucio_mostra_error(env):
    """Export layout sense distribució mostra error."""
    env.window.sidebar.section_changed.emit("classroom")
    env.controller.export_layout()
    assert env.window.errors == [NO_LAYOUT_SELECTED_ERROR]


def test_export_layout_sense_servei_mostra_error(env):
    """Export layout sense servei mostra error."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.export_layout()
    assert env.window.errors == ["L’exportació no està disponible."]


def test_export_layout_genera_el_pdf(env, monkeypatch, tmp_path):
    """Export layout genera el pdf."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.move_student(env.student_a.id, "pending", 0, 0)
    env.controller.reports = env.services.classroom_layout_reports
    destination = tmp_path / "pla.pdf"
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *args: (str(destination), "")
    )

    env.controller.export_layout()

    assert env.window.errors == []
    assert destination.read_bytes().startswith(b"%PDF-")


def test_export_layout_dialeg_cancel_lat_no_fa_res(env, monkeypatch, tmp_path):
    """Export layout diàleg cancel·lat no fa res."""
    env.window.sidebar.section_changed.emit("classroom")
    _blank_layout(env)
    env.controller.reports = env.services.classroom_layout_reports
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))

    env.controller.export_layout()

    assert env.window.errors == []
    assert not (tmp_path / "pla.pdf").exists()
