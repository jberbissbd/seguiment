"""Escenaris compartits i parametrització de les proves d'interfície."""

import os
from types import SimpleNamespace

import pytest

from tutopy.application import create_services
from tutopy.controllers.student_related_controller import StudentRelatedController
from tutopy.database.database import Database
from tutopy.models.messaging import ContactNew, StudentAnnotationNew, StudentNew
from tutopy.ui.main_window import MainWindow


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def student_related_env(qtbot, tmp_path):
    """Prepara un alumne amb les tres classes de dades associades."""
    database = Database(str(tmp_path / "related.db")).connect()
    try:
        services = create_services(database)
        services.documents.storage_dir = tmp_path / "documents"
        student = services.students.create(StudentNew("Laia", "Serra", "4A"))
        annotation = services.annotations.create(StudentAnnotationNew(student.id, "Descriptor"))
        contact = services.contacts.create(ContactNew(student.id, "Marta", "Mare", "", ""))
        source = tmp_path / "informe.txt"
        source.write_text("Informe original", encoding="utf-8")
        document = services.documents.import_file(
            student.id, "Informe", "Trimestral", str(source), "2026-02-01"
        )
        window = MainWindow()
        qtbot.addWidget(window)
        errors = []
        controller = StudentRelatedController(
            window, services.students, services.annotations, services.contacts,
            services.documents, services.academic_courses,
            confirm_delete=lambda _name: True, error_handler=errors.append,
        )
        controller.set_student(student.id)
        yield SimpleNamespace(
            controller=controller, services=services, student=student, window=window,
            errors=errors, annotation=annotation, contact=contact, document=document,
        )
    finally:
        database.close()


@pytest.fixture(params=["annotation", "contact", "document"],
                ids=["descriptor", "contacte", "document"])
def related_kind(request):
    """Executa les garanties compartides per a cada tipus de dada associada."""
    return request.param
