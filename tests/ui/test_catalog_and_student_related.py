from PySide6.QtWidgets import QDialog

from tutopy.application import create_services
from tutopy.controllers.catalog_controller import CategoryController
from tutopy.controllers.student_related_controller import StudentRelatedController
from tutopy.database.database import Database
from tutopy.models.messaging import StudentAnnotationNew, StudentNew
from tutopy.ui.main_window import MainWindow


class AcceptedAnnotationDialog:
    value_to_return = "Descriptor"

    def __init__(self, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def value(self):
        return self.value_to_return


class AcceptedContactDialog:
    values_to_return = {
        "name": "Marta", "description": "Mare",
        "phone": "600000000", "email": "marta@example.cat",
    }

    def __init__(self, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def values(self):
        return dict(self.values_to_return)


class AcceptedDocumentDialog:
    values_to_return = {}

    def __init__(self, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def values(self):
        return dict(self.values_to_return)


class AcceptedTextDialog:
    values = []

    def __init__(self, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def value(self):
        return self.values.pop(0)


def test_controlador_de_dades_relacionades_crea_i_mostra_elements(
    qtbot, tmp_path, monkeypatch
):
    database = Database(str(tmp_path / "student-related.db")).connect()
    try:
        services = create_services(database)
        services.documents.storage_dir = tmp_path / "documents"
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        source = tmp_path / "informe.txt"
        source.write_text("Informe", encoding="utf-8")
        monkeypatch.setattr(AcceptedDocumentDialog, "values_to_return", {
            "name": "Informe", "description": "Trimestral",
            "source_path": str(source), "date": "2026-02-01",
        })
        window = MainWindow()
        qtbot.addWidget(window)
        errors = []
        opened = []
        exported = tmp_path / "exportat.txt"
        controller = StudentRelatedController(
            window, services.students, services.annotations, services.contacts,
            services.documents, services.academic_courses,
            annotation_dialog=AcceptedAnnotationDialog,
            contact_dialog=AcceptedContactDialog,
            document_dialog=AcceptedDocumentDialog,
            confirm_delete=lambda _name: True,
            error_handler=errors.append,
            document_opener=lambda path: opened.append(path) or True,
            export_destination=lambda _filename: str(exported),
        )
        controller.set_student(student.id)

        controller.create_annotation()
        controller.create_contact()
        controller.create_document()

        assert window.student_detail.annotation_tab.list_widget.count() == 1
        assert [label.text() for label in window.student_detail.descriptor_labels] == [
            "Descriptor"
        ]
        services.annotations.create(StudentAnnotationNew(student.id, "Autonomia"))
        controller.refresh_all()
        descriptor_styles = [
            label.styleSheet() for label in window.student_detail.descriptor_labels
        ]
        assert len(set(descriptor_styles)) == 2
        assert window.student_detail.contact_tab.table.rowCount() == 1
        assert window.student_detail.document_tab.table.rowCount() == 1
        document = services.documents.get_by_student(student.id)[0]
        assert (tmp_path / "documents" / document.uuid_filename).exists()
        controller.open_document(document.id)
        controller.export_document(document.id)
        assert opened == [str(tmp_path / "documents" / document.uuid_filename)]
        assert exported.read_text(encoding="utf-8") == "Informe"
        controller.delete_document(document.id)
        assert services.documents.get_by_student(student.id) == []
        assert errors == []
    finally:
        database.close()


def test_controlador_de_categories_fa_crud(qtbot, tmp_path, monkeypatch):
    database = Database(str(tmp_path / "catalogs.db")).connect()
    try:
        services = create_services(database)
        window = MainWindow()
        qtbot.addWidget(window)
        errors = []
        monkeypatch.setattr(AcceptedTextDialog, "values", ["Acadèmic", "Convivència"])
        categories = CategoryController(
            window, services.categories, dialog_factory=AcceptedTextDialog,
            confirm_delete=lambda _name: True, error_handler=errors.append,
        )
        categories.start()

        categories.create()
        category = services.categories.get_all()[0]
        categories.edit(category.id)
        assert services.categories.get_by_id(category.id).name == "Convivència"
        categories.delete(category.id)
        assert services.categories.get_all() == []
        assert errors == []
    finally:
        database.close()


def test_historial_repara_i_mostra_el_grup_inicial(qtbot, tmp_path):
    database = Database(str(tmp_path / "history-repair.db")).connect()
    try:
        services = create_services(database)
        student = database.students.create(StudentNew("Laia", "Martí", "4t B"))
        window = MainWindow()
        qtbot.addWidget(window)
        controller = StudentRelatedController(
            window, services.students, services.annotations, services.contacts,
            services.documents, services.academic_courses,
        )

        controller.set_student(student.id)

        table = window.student_detail.history_tab.table
        assert table.rowCount() == 1
        assert table.item(0, 0).text() == "4t B"
        assert table.item(0, 1).text() != "—"
        assert table.item(0, 3).text() == "Actual"
    finally:
        database.close()


def test_colors_dels_descriptors_son_globals_i_estables(qtbot, tmp_path):
    database = Database(str(tmp_path / "descriptor-colors.db")).connect()
    try:
        services = create_services(database)
        first_student = services.students.create(StudentNew("Laia", "Martí", "4t A"))
        second_student = services.students.create(StudentNew("Jordi", "Puig", "4t B"))
        first = services.annotations.create(
            StudentAnnotationNew(first_student.id, "Autonomia")
        )
        second = services.annotations.create(
            StudentAnnotationNew(second_student.id, "Autonomia")
        )
        window = MainWindow()
        qtbot.addWidget(window)
        controller = StudentRelatedController(
            window, services.students, services.annotations, services.contacts,
            services.documents, services.academic_courses,
        )

        controller.set_student(first_student.id)
        first_style = window.student_detail.descriptor_labels[0].styleSheet()
        controller.set_student(second_student.id)
        second_style = window.student_detail.descriptor_labels[0].styleSheet()
        controller.set_student(first_student.id)
        first_style_again = window.student_detail.descriptor_labels[0].styleSheet()

        assert first.id != second.id
        assert first_style != second_style
        assert first_style_again == first_style
    finally:
        database.close()
