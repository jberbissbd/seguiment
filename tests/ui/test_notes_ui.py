from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDialog

from tutopy.application import create_services
from tutopy.controllers.note_controller import NoteController
from tutopy.database.database import Database
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
from tutopy.services.exceptions import ValidationError
from tutopy.ui.dialogs.note_dialog import NoteDialog
from tutopy.ui.main_window import MainWindow
from tutopy.ui.tabs.notes_tab import NotesTab


class AcceptedNoteDialog:
    values_to_return = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def exec(self):
        return QDialog.DialogCode.Accepted

    def values(self):
        return dict(self.values_to_return)


class RejectedNoteDialog(AcceptedNoteDialog):
    def exec(self):
        return QDialog.DialogCode.Rejected


def build_note_controller(qtbot, tmp_path, confirm_delete=lambda: True):
    """Construeix l'escenari d'UI compartit per les proves de notes."""
    database = Database(str(tmp_path / "notes-ui.db")).connect()
    services = create_services(database)
    student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    window = MainWindow()
    qtbot.addWidget(window)
    errors = []
    controller = NoteController(
        window,
        services.notes,
        services.categories,
        services.academic_courses,
        dialog_factory=AcceptedNoteDialog,
        confirm_delete=confirm_delete,
        error_handler=errors.append,
    )
    controller.start()
    controller.set_student_context(student.id)
    return database, services, student, category, window, controller, errors


def test_note_dialog_retorna_valors_valids(qtbot):
    database = Database(":memory:").connect()
    try:
        services = create_services(database)
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        category = services.categories.create(CategoryNew("Acadèmic"))
        dialog = NoteDialog(
            student_id=student.id, categories=[category]
        )
        qtbot.addWidget(dialog)
        dialog.date_input.setDate(QDate(2026, 1, 15))
        dialog.content_input.setPlainText("  Seguiment positiu  ")

        dialog._accept_valid()

        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.values() == {
            "student_id": student.id,
            "category_id": category.id,
            "date": "2026-01-15",
            "course_id": 0,
            "content": "Seguiment positiu",
        }
    finally:
        database.close()


def test_note_dialog_accepta_la_data_escrita_directament(qtbot):
    database = Database(":memory:").connect()
    try:
        services = create_services(database)
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        category = services.categories.create(CategoryNew("Acadèmic"))
        dialog = NoteDialog(student_id=student.id, categories=[category])
        qtbot.addWidget(dialog)
        editor = dialog.date_input.lineEdit()

        editor.selectAll()
        qtbot.keyClicks(editor, "15/01/2026")
        dialog.date_input.interpretText()
        dialog.content_input.setPlainText("Seguiment")

        assert dialog.values()["date"] == "2026-01-15"
    finally:
        database.close()


def test_notes_tab_construeix_filtres_combinables(qtbot):
    database = Database(":memory:").connect()
    try:
        services = create_services(database)
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        category = services.categories.create(CategoryNew("Acadèmic"))
        course = services.academic_courses.get_or_create("2025-2026")
        tab = NotesTab()
        qtbot.addWidget(tab)
        tab.set_options([category], [course])
        tab.set_student_context(student.id)
        tab.category_filter.setCurrentIndex(1)
        tab.course_filter.setCurrentIndex(1)
        tab.date_from.setDate(QDate(2026, 1, 1))
        tab.date_from_enabled.setChecked(True)
        tab.content_filter.setText("progrés")

        filters = tab.filters()
        assert filters["student_id"] == student.id
        assert filters["category_id"] == category.id
        assert filters["course_id"] == course.id
        assert filters["date_from"] == "2026-01-01"
        assert filters["content"] == "progrés"
    finally:
        database.close()


def test_note_controller_crud(qtbot, tmp_path, monkeypatch):
    database, services, student, category, window, controller, errors = (
        build_note_controller(qtbot, tmp_path)
    )
    try:
        monkeypatch.setattr(AcceptedNoteDialog, "values_to_return", {
            "student_id": student.id,
            "category_id": category.id,
            "date": "2026-01-15",
            "course_id": 0,
            "content": "Nota inicial",
        })
        controller.create()
        notes = services.notes.get_all()
        assert len(notes) == 1
        assert controller.view.table.rowCount() == 1

        monkeypatch.setattr(AcceptedNoteDialog, "values_to_return", {
            "student_id": student.id,
            "category_id": category.id,
            "date": "2026-02-10",
            "course_id": 0,
            "content": "Nota actualitzada",
        })
        controller.edit(notes[0].id)
        assert services.notes.get_by_id(notes[0].id).content == "Nota actualitzada"

        controller.delete(notes[0].id)
        assert services.notes.get_all() == []
        assert controller.view.table.rowCount() == 0
        assert errors == []
    finally:
        database.close()


def test_accio_contextual_crea_la_nota_per_l_alumne_de_la_fila(
    qtbot, tmp_path, monkeypatch
):
    database, services, first, category, window, controller, errors = (
        build_note_controller(qtbot, tmp_path)
    )
    try:
        second = services.students.create(StudentNew("Anna", "Serra", "3r B"))
        window.student_list.set_students([first, second])
        monkeypatch.setattr(AcceptedNoteDialog, "values_to_return", {
            "student_id": first.id,
            "category_id": category.id,
            "date": "2026-01-15",
            "course_id": 0,
            "content": "Nota des de la fila",
        })
        second_item = window.student_list.list_widget.item(1)
        second_widget = window.student_list.list_widget.itemWidget(second_item)
        second_widget.set_selected(True)

        qtbot.mouseClick(second_widget.note_button, Qt.MouseButton.LeftButton)

        note = services.notes.get_all()[0]
        assert note.student_id == second.id
        assert controller.current_student_id == second.id
        assert not hasattr(controller.view, "create_button")
        assert errors == []
    finally:
        database.close()


def test_note_controller_aplica_filtres_de_la_vista(qtbot, tmp_path):
    database, services, student, category, window, controller, errors = (
        build_note_controller(qtbot, tmp_path)
    )
    try:
        other_category = services.categories.create(CategoryNew("Conducta"))
        services.notes.create(NoteNew(
            student.id, category.id, "2026-01-15", 0, "Progrés notable"
        ))
        services.notes.create(NoteNew(
            student.id, other_category.id, "2026-01-20", 0, "Incidència"
        ))
        controller.refresh_options()
        controller.view.set_student_context(student.id)
        controller.view.category_filter.setCurrentIndex(
            controller.view.category_filter.findData(category.id)
        )
        controller.view.content_filter.setText("notable")

        qtbot.waitUntil(
            lambda: controller.view.table.rowCount() == 1,
            timeout=1_000,
        )

        assert controller.view.table.rowCount() == 1
        assert controller.view.table.columnCount() == 3
        assert controller.view.table.item(0, 2).text() == "Progrés notable"
        assert errors == []
    finally:
        database.close()


def test_note_controller_valida_context_categoria_i_cancel_lacions(
    qtbot, tmp_path
):
    database, services, student, category, _window, controller, errors = (
        build_note_controller(qtbot, tmp_path, confirm_delete=lambda: False)
    )
    try:
        controller.current_student_id = None
        controller.create()
        assert "seleccionar un alumne" in errors.pop()

        controller.current_student_id = student.id
        services.categories.category_dao.delete(category.id)
        controller.create()
        assert "crear una categoria" in errors.pop()

        replacement = services.categories.create(CategoryNew("Acadèmic"))
        controller.dialog_factory = RejectedNoteDialog
        controller.create()
        assert services.notes.get_all() == []

        note = services.notes.create(NoteNew(
            student.id, replacement.id, "2026-01-15", 0, "Nota"
        ))
        controller.edit(note.id)
        controller.delete(note.id)
        assert services.notes.get_by_id(note.id) is not None
    finally:
        database.close()


def test_note_controller_mostra_errors_de_servei(qtbot, tmp_path):
    database, services, student, category, _window, controller, errors = (
        build_note_controller(qtbot, tmp_path)
    )
    try:
        controller.note_service.get_records = lambda *_args: (
            (_ for _ in ()).throw(ValidationError("filtre incorrecte"))
        )
        controller.refresh()

        controller.note_service.get_by_id = lambda _id: (
            (_ for _ in ()).throw(ValidationError("nota inexistent"))
        )
        controller.edit(999)

        controller.note_service.delete = lambda _id: (
            (_ for _ in ()).throw(ValidationError("no es pot eliminar"))
        )
        controller.delete(999)

        assert errors == [
            "filtre incorrecte", "nota inexistent", "no es pot eliminar",
        ]
    finally:
        database.close()
