from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QLabel

from tutopy.models.messaging import Student
from tutopy.models.pdf_photo_import import (
    PdfPhotoCaption, PdfPhotoEntry, PdfPhotoImportPreview,
)
from tutopy.ui.dialogs.pdf_photo_import_dialog import SKIP_LABEL, PdfPhotoImportDialog


def _write_jpg(tmp_path, name="foto.jpg"):
    path = tmp_path / name
    pixmap = QPixmap(10, 10)
    pixmap.fill(QColor("blue"))
    pixmap.save(str(path), "JPG")
    return path


def _students():
    return [
        Student(1, "u1", "Berta", "Pons Fictícia", "1r Batx C"),
        Student(2, "u2", "Jan", "Soler Exemple", "1r Batx C"),
    ]


def test_preselecciona_l_alumne_preassignat(qtbot, tmp_path):
    image_path = str(_write_jpg(tmp_path))
    preview = PdfPhotoImportPreview(
        entries=(
            PdfPhotoEntry(
                PdfPhotoCaption(1, "Pons Fictícia", "Berta"), image_path,
                matched_student_id=1,
            ),
        ),
        missing_photos=(),
        temp_dir=str(tmp_path),
    )
    dialog = PdfPhotoImportDialog(preview, _students())
    qtbot.addWidget(dialog)
    assert dialog.assignments() == {1: 1}


def test_sense_coincidencia_queda_a_ometre(qtbot, tmp_path):
    image_path = str(_write_jpg(tmp_path))
    preview = PdfPhotoImportPreview(
        entries=(
            PdfPhotoEntry(
                PdfPhotoCaption(7, "Desconegut", "Algú"), image_path,
                matched_student_id=None,
            ),
        ),
        missing_photos=(),
        temp_dir=str(tmp_path),
    )
    dialog = PdfPhotoImportDialog(preview, _students())
    qtbot.addWidget(dialog)
    combo = dialog._combos[7]
    assert combo.currentText() == SKIP_LABEL
    assert dialog.assignments() == {7: None}


def test_assignments_reflecteix_un_canvi_manual(qtbot, tmp_path):
    image_path = str(_write_jpg(tmp_path))
    preview = PdfPhotoImportPreview(
        entries=(
            PdfPhotoEntry(
                PdfPhotoCaption(1, "Pons Fictícia", "Berta"), image_path,
                matched_student_id=None,
            ),
        ),
        missing_photos=(),
        temp_dir=str(tmp_path),
    )
    dialog = PdfPhotoImportDialog(preview, _students())
    qtbot.addWidget(dialog)
    combo = dialog._combos[1]
    combo.setCurrentIndex(combo.findData(2))
    assert dialog.assignments() == {1: 2}


def test_mostra_avis_dels_alumnes_sense_fotografia(qtbot, tmp_path):
    image_path = str(_write_jpg(tmp_path))
    preview = PdfPhotoImportPreview(
        entries=(
            PdfPhotoEntry(PdfPhotoCaption(1, "Pons Fictícia", "Berta"), image_path),
        ),
        missing_photos=(PdfPhotoCaption(2, "Roig Provatura", "Martí"),),
        temp_dir=str(tmp_path),
    )
    dialog = PdfPhotoImportDialog(preview, _students())
    qtbot.addWidget(dialog)
    texts = [label.text() for label in dialog.findChildren(QLabel)]
    assert any("Martí Roig Provatura" in text for text in texts)
