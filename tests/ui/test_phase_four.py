from PySide6.QtWidgets import QDialog

from tutopy.application import create_services
from tutopy.controllers.catalog_controller import (
    AcademicCourseController, CategoryController,
)
from tutopy.controllers.student_related_controller import StudentRelatedController
from tutopy.database.database import Database
from tutopy.models.messaging import StudentNew
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


def test_controlador_de_dades_relacionades_crea_i_mostra_elements(qtbot, tmp_path):
    database = Database(str(tmp_path / "phase-four.db")).connect()
    try:
        services = create_services(database)
        services.documents.storage_dir = tmp_path / "documents"
        student = services.students.create(StudentNew("Jordi", "Garcia", "4t A"))
        source = tmp_path / "informe.txt"
        source.write_text("Informe", encoding="utf-8")
        AcceptedDocumentDialog.values_to_return = {
            "name": "Informe", "description": "Trimestral",
            "source_path": str(source),
        }
        window = MainWindow()
        qtbot.addWidget(window)
        errors = []
        controller = StudentRelatedController(
            window, services.students, services.annotations, services.contacts,
            services.documents, services.academic_courses,
            annotation_dialog=AcceptedAnnotationDialog,
            contact_dialog=AcceptedContactDialog,
            document_dialog=AcceptedDocumentDialog,
            confirm_delete=lambda _name: True,
            error_handler=errors.append,
        )
        controller.set_student(student.id)

        controller.create_annotation()
        controller.create_contact()
        controller.create_document()

        assert window.student_detail.annotation_tab.list_widget.count() == 1
        assert window.student_detail.contact_tab.table.rowCount() == 1
        assert window.student_detail.document_tab.table.rowCount() == 1
        document = services.documents.get_by_student(student.id)[0]
        assert (tmp_path / "documents" / document.uuid_filename).exists()
        controller.delete_document(document.id)
        assert services.documents.get_by_student(student.id) == []
        assert errors == []
    finally:
        database.close()


def test_controladors_de_categories_i_cursos_fan_crud(qtbot, tmp_path):
    database = Database(str(tmp_path / "catalogs.db")).connect()
    try:
        services = create_services(database)
        window = MainWindow()
        qtbot.addWidget(window)
        errors = []
        AcceptedTextDialog.values = ["Acadèmic", "Convivència", "2025-2026", "2026-2027"]
        categories = CategoryController(
            window, services.categories, dialog_factory=AcceptedTextDialog,
            confirm_delete=lambda _name: True, error_handler=errors.append,
        )
        courses = AcademicCourseController(
            window, services.academic_courses, dialog_factory=AcceptedTextDialog,
            confirm_delete=lambda _name: True, error_handler=errors.append,
        )
        categories.start()
        courses.start()

        categories.create()
        category = services.categories.get_all()[0]
        categories.edit(category.id)
        courses.create()
        course = services.academic_courses.get_all()[0]
        courses.edit(course.id)

        assert services.categories.get_by_id(category.id).name == "Convivència"
        assert services.academic_courses.get_by_id(course.id).course == "2026-2027"
        categories.delete(category.id)
        courses.delete(course.id)
        assert services.categories.get_all() == []
        assert services.academic_courses.get_all() == []
        assert errors == []
    finally:
        database.close()
