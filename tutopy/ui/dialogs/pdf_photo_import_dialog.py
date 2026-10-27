"""Diàleg per revisar i confirmar l'aparellament de fotos extretes d'un PDF."""

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QCompleter, QHeaderView, QLabel,
    QTableWidget, QTableWidgetItem, QWidget,
)

from tutopy.models.messaging import Student
from tutopy.models.pdf_photo_import import PdfPhotoImportPreview
from tutopy.ui.dialogs._base_form_dialog import BaseFormDialog

SKIP_LABEL = "— Ometre —"
THUMBNAIL_SIZE = 56


class PdfPhotoImportDialog(BaseFormDialog):
    """Mostra cada fotografia extreta amb l'alumne de Tutopy preassignat.

    No s'aplica cap canvi en acceptar aquest diàleg: el controlador és qui,
    un cop obtingudes les decisions amb :meth:`assignments`, desa
    efectivament les fotos via `PhotoService`.
    """

    def __init__(
        self, preview: PdfPhotoImportPreview, students: Sequence[Student],
        parent: QWidget | None = None,
    ):
        """Construeix una fila per fotografia extreta.

        Args:
            preview: Resultat de `PdfPhotoImportService.parse`.
            students: Alumnes existents per emplenar els desplegables.
            parent: Widget pare de Qt, si escau.
        """
        super().__init__(parent, "Revisar fotos importades del PDF")
        self.setMinimumSize(820, 560)
        self._nums = [entry.caption.num for entry in preview.entries]
        self._combos: dict[int, QComboBox] = {}

        description = QLabel(
            "Revisa l’aparellament abans de confirmar. Les files sense "
            "alumne coincident es poden assignar manualment o ometre."
        )
        description.setWordWrap(True)
        self.layout.addWidget(description)

        sorted_students = sorted(students, key=lambda student: student.filing_name)

        self.table = QTableWidget(len(preview.entries), 3)
        self.table.setHorizontalHeaderLabels(("Foto", "Al PDF", "Alumne de Tutopy"))
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for row, entry in enumerate(preview.entries):
            self.table.setRowHeight(row, THUMBNAIL_SIZE + 8)
            thumbnail = QLabel()
            pixmap = QPixmap(entry.image_path)
            if not pixmap.isNull():
                thumbnail.setPixmap(pixmap.scaled(
                    THUMBNAIL_SIZE, THUMBNAIL_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
            self.table.setCellWidget(row, 0, thumbnail)
            self.table.setItem(row, 1, QTableWidgetItem(entry.caption.full_name))
            combo = self._build_combo(sorted_students, entry.matched_student_id)
            self.table.setCellWidget(row, 2, combo)
            self._combos[entry.caption.num] = combo
        self.layout.addWidget(self.table, 1)

        if preview.missing_photos:
            names = ", ".join(caption.full_name for caption in preview.missing_photos)
            warning = QLabel(
                f"Sense fotografia al PDF ({len(preview.missing_photos)}): {names}"
            )
            warning.setObjectName("mutedText")
            warning.setWordWrap(True)
            self.layout.addWidget(warning)

        self._add_footer("", save_text="Confirmar")

    @staticmethod
    def _build_combo(students: Sequence[Student], matched_student_id: int | None) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.addItem(SKIP_LABEL, None)
        for student in students:
            label = (
                f"{student.filing_name} — {student.group_name}"
                if student.group_name else student.filing_name
            )
            combo.addItem(label, student.id)
        completer = QCompleter([combo.itemText(index) for index in range(combo.count())])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        combo.setCompleter(completer)
        if matched_student_id is not None:
            index = combo.findData(matched_student_id)
            if index >= 0:
                combo.setCurrentIndex(index)
        return combo

    def _is_valid(self) -> bool:
        return True

    def assignments(self) -> dict[int, int | None]:
        """Retorna, per número d'entrada, l'alumne triat o `None` si s'omet."""
        return {num: combo.currentData() for num, combo in self._combos.items()}
