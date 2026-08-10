from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSizePolicy, QTabWidget, QVBoxLayout, QWidget,
)

from tutopy.ui.tabs.annotation_tab import AnnotationTab
from tutopy.ui.tabs.contact_tab import ContactTab
from tutopy.ui.tabs.document_tab import DocumentTab
from tutopy.ui.tabs.history_tab import HistoryTab
from tutopy.ui.tabs.notes_tab import NotesTab
from tutopy.ui.widgets.avatar import avatar_stylesheet, initials
from tutopy.ui.widgets.flow_layout import FlowLayout
from tutopy.ui.resources import icon


class StudentDetailPanel(QFrame):
    """Capçalera i pestanyes de detall de l'alumne seleccionat."""

    TAB_NAMES = ("Notes", "Descriptors", "Contactes", "Documents", "Històric")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.current_student_id = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.placeholder = QLabel("Selecciona un alumne per consultar-ne el detall.")
        self.placeholder.setObjectName("mutedText")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder, 1)

        self.student_summary = QFrame()
        self.student_summary.setObjectName("studentSummary")
        info_layout = QHBoxLayout(self.student_summary)
        info_layout.setContentsMargins(18, 14, 18, 14)
        info_layout.setSpacing(14)

        self.avatar_value = QLabel()
        self.avatar_value.setObjectName("studentAvatar")
        self.avatar_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_value.setFixedSize(46, 46)
        info_layout.addWidget(self.avatar_value)

        identity_layout = QVBoxLayout()
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(3)
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(10)
        self.name_value = QLabel()
        self.name_value.setObjectName("studentName")
        name_layout.addWidget(self.name_value)

        self.descriptor_container = QWidget()
        self.descriptor_container.setMaximumWidth(360)
        self.descriptor_container.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding
        )
        self.descriptor_flow = FlowLayout(self.descriptor_container)
        self.descriptor_labels = []
        name_layout.addWidget(self.descriptor_container, 1)
        name_layout.addStretch()

        self.group_value = QLabel()
        self.group_value.setObjectName("studentMeta")
        identity_layout.addLayout(name_layout)
        identity_layout.addWidget(self.group_value)
        info_layout.addLayout(identity_layout, 1)

        self.student_summary.hide()
        layout.addWidget(self.student_summary)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setIconSize(QSize(18, 18))
        self.notes_tab = NotesTab()
        self.annotation_tab = AnnotationTab()
        self.contact_tab = ContactTab()
        self.document_tab = DocumentTab()
        self.history_tab = HistoryTab()
        self.tabs.addTab(self.notes_tab, icon("notes.svg"), "Notes")
        self.tabs.addTab(self.annotation_tab, icon("descriptors.svg"), "Descriptors")
        self.tabs.addTab(self.contact_tab, icon("contacts.svg"), "Contactes")
        self.tabs.addTab(self.document_tab, icon("documents.svg"), "Documents")
        self.tabs.addTab(self.history_tab, icon("history.svg"), "Històric")
        self.tabs.hide()
        layout.addWidget(self.tabs, 1)

    def show_student(self, student) -> None:
        if student is None:
            self.clear()
            return
        self.current_student_id = student.id
        self.avatar_value.setText(initials(student.name, student.surnames))
        self.avatar_value.setStyleSheet(avatar_stylesheet(student.id, 23))
        self.name_value.setText(student.full_name)
        self.group_value.setText(student.group_name or "Sense grup assignat")
        self.placeholder.hide()
        self.student_summary.show()
        self.tabs.show()

    def clear(self) -> None:
        self.current_student_id = None
        self.set_descriptors([])
        self.student_summary.hide()
        self.tabs.hide()
        self.placeholder.show()

    def set_descriptors(self, descriptors) -> None:
        self.descriptor_flow.clear()
        self.descriptor_labels = []
        if not descriptors:
            label = QLabel("Sense descriptors")
            label.setStyleSheet(
                "background-color: #F1F5F9; color: #64748B; border: none; "
                "border-radius: 5px; padding: 5px 8px; font-size: 12px;"
            )
            self.descriptor_flow.addWidget(label)
            self.descriptor_labels.append(label)
            return
        for descriptor in descriptors:
            content = descriptor.content
            label = QLabel(self._short_text(content))
            label.setToolTip(content)
            background, foreground = self._descriptor_colors(descriptor.id)
            label.setStyleSheet(
                f"background-color: {background}; color: {foreground}; "
                "border: none; border-radius: 5px; padding: 5px 8px; font-size: 12px;"
            )
            self.descriptor_flow.addWidget(label)
            self.descriptor_labels.append(label)

    @staticmethod
    def _short_text(content: str, limit: int = 42) -> str:
        return content if len(content) <= limit else f"{content[:limit - 1]}…"

    @staticmethod
    def _descriptor_colors(descriptor_id: int) -> tuple[str, str]:
        """Genera un parell estable i contrastat des de l'ID global."""
        hue = round((descriptor_id * 137.508) % 360)
        background = QColor.fromHsl(hue, 145, 226).name()
        foreground = QColor.fromHsl(hue, 210, 62).name()
        return background, foreground
