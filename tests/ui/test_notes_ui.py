from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog

from tutopy.application import create_services
from tutopy.controllers.note_controller import NoteController
from tutopy.database.database import Database
from tutopy.models.messaging import CategoryNew, NoteNew, StudentNew
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

        dialog._validate_and_accept()

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


def test_note_controller_crud(qtbot, tmp_path):
    database, services, student, category, window, controller, errors = (
        build_note_controller(qtbot, tmp_path)
    )
    try:
        AcceptedNoteDialog.values_to_return = {
            "student_id": student.id,
            "category_id": category.id,
            "date": "2026-01-15",
            "course_id": 0,
            "content": "Nota inicial",
        }
        controller.create()
        notes = services.notes.get_all()
        assert len(notes) == 1
        assert controller.view.table.rowCount() == 1

        AcceptedNoteDialog.values_to_return = {
            "student_id": student.id,
            "category_id": category.id,
            "date": "2026-02-10",
            "course_id": 0,
            "content": "Nota actualitzada",
        }
        controller.edit(notes[0].id)
        assert services.notes.get_by_id(notes[0].id).content == "Nota actualitzada"

        controller.delete(notes[0].id)
        assert services.notes.get_all() == []
        assert controller.view.table.rowCount() == 0
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

        assert controller.view.table.rowCount() == 1
        assert controller.view.table.columnCount() == 3
        assert controller.view.table.item(0, 2).text() == "Progrés notable"
        assert errors == []
    finally:
        database.close()
