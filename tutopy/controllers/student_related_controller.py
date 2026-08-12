from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QFileDialog

from tutopy.models.messaging import (
    Contact, ContactNew, StudentAnnotation, StudentAnnotationNew, StudentDocument,
)
from tutopy.services.annotation_service import AnnotationService
from tutopy.services.academic_course_service import AcademicCourseService
from tutopy.services.contact_service import ContactService
from tutopy.services.document_service import DocumentService
from tutopy.services.exceptions import DomainError
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.annotation_dialog import AnnotationDialog
from tutopy.ui.dialogs.contact_dialog import ContactDialog
from tutopy.ui.dialogs.document_dialog import DocumentDialog
from tutopy.ui.main_window import MainWindow


class StudentRelatedController:
    """Gestiona descriptors, contactes, documents i historial de l'alumne."""

    def __init__(self, window: MainWindow, students: StudentService,
        annotations: AnnotationService, contacts: ContactService,
        documents: DocumentService, courses: AcademicCourseService,
        annotation_dialog=AnnotationDialog,
        contact_dialog=ContactDialog, document_dialog=DocumentDialog,
        confirm_delete=None, error_handler=None, document_opener=None,
        export_destination=None):
        self.window = window
        self.students = students
        self.annotations = annotations
        self.contacts = contacts
        self.documents = documents
        self.courses = courses
        self.annotation_dialog = annotation_dialog
        self.contact_dialog = contact_dialog
        self.document_dialog = document_dialog
        self.confirm_delete = confirm_delete or window.confirm_deletion
        self.error_handler = error_handler or window.show_error
        self.document_opener = document_opener or self._open_local_file
        self.export_destination = export_destination or self._choose_export_destination
        self.student_id = None
        self._connect()

    def _connect(self):
        self.window.student_list.student_selected.connect(self.set_student)
        annotation = self.window.student_detail.annotation_tab
        annotation.create_requested.connect(self.create_annotation)
        annotation.edit_requested.connect(self.edit_annotation)
        annotation.delete_requested.connect(self.delete_annotation)
        contact = self.window.student_detail.contact_tab
        contact.create_requested.connect(self.create_contact)
        contact.edit_requested.connect(self.edit_contact)
        contact.delete_requested.connect(self.delete_contact)
        document = self.window.student_detail.document_tab
        document.create_requested.connect(self.create_document)
        document.edit_requested.connect(self.edit_document)
        document.delete_requested.connect(self.delete_document)
        document.open_requested.connect(self.open_document)
        document.export_requested.connect(self.export_document)

    def set_student(self, student_id: int):
        self.student_id = student_id
        self.refresh_all()

    def refresh_all(self):
        if self.student_id is None:
            return
        annotations = self.annotations.get_by_student(self.student_id)
        self.window.student_detail.set_descriptors(annotations)
        self.window.student_detail.annotation_tab.set_items(
            [(item.id, item.content) for item in annotations]
        )
        contacts = self.contacts.get_by_student(self.student_id)
        self.window.student_detail.contact_tab.set_rows([
            (item.id, (item.name, item.description, item.phone, item.email))
            for item in contacts
        ])
        documents = self.documents.get_by_student(self.student_id)
        self.window.student_detail.document_tab.set_rows([
            (item.id, (item.date or "—", item.name, item.description, item.original_filename))
            for item in documents
        ])
        history = self.students.get_group_history(self.student_id)
        courses = {course.id: course.course for course in self.courses.get_all()}
        self.window.student_detail.history_tab.set_history([
            (item.group_name, courses.get(item.academic_course_id, "—"),
             item.start_date, item.end_date or "Actual")
            for item in history
        ])

    def create_annotation(self):
        if self.student_id is None:
            return
        dialog = self.annotation_dialog(parent=self.window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._run(lambda: self.annotations.create(
            StudentAnnotationNew(self.student_id, dialog.value())
        ), "Descriptor creat")

    def edit_annotation(self, entity_id):
        annotation = self.annotations.get_by_id(entity_id)
        dialog = self.annotation_dialog(parent=self.window, annotation=annotation)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self.annotations.update(StudentAnnotation(
                annotation.id, annotation.student_id, dialog.value()
            )), "Descriptor actualitzat")

    def delete_annotation(self, entity_id):
        if self.confirm_delete("aquest descriptor"):
            self._run(lambda: self.annotations.delete(entity_id), "Descriptor eliminat")

    def create_contact(self):
        if self.student_id is None:
            return
        dialog = self.contact_dialog(parent=self.window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self.contacts.create(ContactNew(
                student_id=self.student_id, **dialog.values()
            )), "Contacte creat")

    def edit_contact(self, entity_id):
        contact = self.contacts.get_by_id(entity_id)
        dialog = self.contact_dialog(parent=self.window, contact=contact)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run(lambda: self.contacts.update(Contact(
                id=contact.id, student_id=contact.student_id, **dialog.values()
            )), "Contacte actualitzat")

    def delete_contact(self, entity_id):
        if self.confirm_delete("aquest contacte"):
            self._run(lambda: self.contacts.delete(entity_id), "Contacte eliminat")

    def create_document(self):
        if self.student_id is None:
            return
        dialog = self.document_dialog(parent=self.window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.values()
            self._run(lambda: self.documents.import_file(
                self.student_id, values["name"], values["description"],
                values["source_path"],
                values["date"],
            ), "Document importat")

    def edit_document(self, entity_id):
        document = self.documents.get_by_id(entity_id)
        dialog = self.document_dialog(parent=self.window, document=document)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.values()
            updated = StudentDocument(
                id=document.id, student_id=document.student_id,
                name=values["name"], description=values["description"],
                uuid_filename=document.uuid_filename,
                original_filename=document.original_filename,
                file_path=document.file_path,
                date=values["date"], course_id=document.course_id,
            )
            self._run(lambda: self.documents.update(updated), "Document actualitzat")

    def delete_document(self, entity_id):
        if self.confirm_delete("aquest document"):
            self._run(lambda: self.documents.delete(entity_id), "Document eliminat")

    def open_document(self, entity_id):
        try:
            path = self.documents.get_readable_path(entity_id)
            opened = self.document_opener(str(path))
            if opened is False:
                self.error_handler("No s'ha trobat cap aplicació per obrir el document.")
        except DomainError as error:
            self.error_handler(str(error))

    def export_document(self, entity_id):
        try:
            document = self.documents.get_by_id(entity_id)
            destination = self.export_destination(document.original_filename)
            if not destination:
                return
            self.documents.export_file(entity_id, destination)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.window.show_status("Document exportat")

    @staticmethod
    def _open_local_file(path):
        return QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _choose_export_destination(self, filename):
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Exportar document", filename
        )
        return path

    def _run(self, operation, success_message):
        try:
            operation()
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.refresh_all()
        self.window.show_status(success_message)
