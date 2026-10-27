from pathlib import Path

import pymupdf
import pytest

from tutopy.models.messaging import StudentNew
from tutopy.services.exceptions import ValidationError
from tutopy.services.pdf_photo_import_service import PdfPhotoImportService


def _solid_pixmap(width, height, color):
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, width, height), False)
    pix.set_rect(pix.irect, color)
    return pix


def _build_orla_pdf(path: Path) -> None:
    """Construeix un PDF sintètic de 2 pàgines que imita el format "orla".

    Graella de 2 columnes x 2 files a la pàgina 1, amb una fotografia
    deliberadament absent (fila 0, columna 1) per provar que l'aparellament
    per graella no es desquadra; una pàgina 2 amb una fila més per provar
    que la numeració continua entre pàgines. També s'hi afegeix un logotip
    molt més ample que alt, que s'ha de descartar com a fotografia.
    """
    doc = pymupdf.open()
    page1 = doc.new_page(width=600, height=400)
    logo = _solid_pixmap(150, 30, (200, 200, 200))
    page1.insert_image(pymupdf.Rect(20, 10, 170, 40), pixmap=logo)

    photo1 = _solid_pixmap(40, 60, (255, 0, 0))
    page1.insert_image(pymupdf.Rect(50, 100, 90, 160), pixmap=photo1)
    page1.insert_text((50, 175), "1.  Pons Fictícia, Berta")
    # Fila 0, columna 1: etiqueta sense fotografia (cel·la buida al PDF real).
    page1.insert_text((250, 175), "2.  Roig Provatura, Martí")

    photo3 = _solid_pixmap(40, 60, (0, 255, 0))
    page1.insert_image(pymupdf.Rect(50, 250, 90, 310), pixmap=photo3)
    page1.insert_text((50, 325), "3.  Soler Exemple, Jan")
    photo4 = _solid_pixmap(40, 60, (0, 0, 255))
    page1.insert_image(pymupdf.Rect(250, 250, 290, 310), pixmap=photo4)
    page1.insert_text((250, 325), "4.  Vila Mostra, Queralt")

    page2 = doc.new_page(width=600, height=400)
    logo2 = _solid_pixmap(150, 30, (200, 200, 200))
    page2.insert_image(pymupdf.Rect(20, 10, 170, 40), pixmap=logo2)
    photo5 = _solid_pixmap(40, 60, (255, 255, 0))
    page2.insert_image(pymupdf.Rect(50, 100, 90, 160), pixmap=photo5)
    page2.insert_text((50, 175), "5.  Ferran Inventada, Nora")

    doc.save(str(path))
    doc.close()


@pytest.fixture
def orla_pdf(tmp_path) -> Path:
    path = tmp_path / "orla.pdf"
    _build_orla_pdf(path)
    return path


def test_parse_apparella_per_graella_i_salta_la_cel_la_buida(db, orla_pdf):
    """Les fotos s'aparellen amb la seva etiqueta per posició, no per ordre."""
    service = PdfPhotoImportService(_students_service(db))
    preview = service.parse(orla_pdf)
    try:
        nums = [entry.caption.num for entry in preview.entries]
        assert nums == [1, 3, 4, 5]
        assert [caption.num for caption in preview.missing_photos] == [2]

        by_num = {entry.caption.num: entry for entry in preview.entries}
        assert by_num[1].caption.surnames == "Pons Fictícia"
        assert by_num[1].caption.name == "Berta"
        assert by_num[4].caption.surnames == "Vila Mostra"
        assert by_num[4].caption.name == "Queralt"
        # La numeració continua a la pàgina 2 (no es reinicia a 1).
        assert by_num[5].caption.surnames == "Ferran Inventada"

        for entry in preview.entries:
            assert Path(entry.image_path).is_file()
    finally:
        service.cleanup(preview)
    assert not Path(preview.temp_dir).exists()


def test_parse_descarta_el_logotip_com_a_fotografia(db, orla_pdf):
    """El logotip (molt més ample que alt) no es confon amb cap fotografia."""
    service = PdfPhotoImportService(_students_service(db))
    preview = service.parse(orla_pdf)
    try:
        assert len(preview.entries) == 4
    finally:
        service.cleanup(preview)


def test_parse_preassigna_coincidencia_exacta_i_unica(db, orla_pdf):
    """Un nom normalitzat que coincideix amb un únic alumne es preassigna."""
    student = db.students.create(StudentNew("Berta", "Pons Fictícia", "1r Batx C"))
    service = PdfPhotoImportService(_students_service(db))
    preview = service.parse(orla_pdf)
    try:
        by_num = {entry.caption.num: entry for entry in preview.entries}
        assert by_num[1].matched_student_id == student.id
        assert by_num[3].matched_student_id is None
    finally:
        service.cleanup(preview)


def test_parse_no_preassigna_coincidencia_ambigua(db, orla_pdf):
    """Dos alumnes amb el mateix nom normalitzat no es preassignen automàticament."""
    db.students.create(StudentNew("Berta", "Pons Fictícia", "1r Batx C"))
    db.students.create(StudentNew("Berta", "Pons Fictícia", "1r Batx D"))
    service = PdfPhotoImportService(_students_service(db))
    preview = service.parse(orla_pdf)
    try:
        by_num = {entry.caption.num: entry for entry in preview.entries}
        assert by_num[1].matched_student_id is None
    finally:
        service.cleanup(preview)


def test_parse_rebutja_fitxer_inexistent(db, tmp_path):
    """parse() rebutja una ruta que no existeix."""
    service = PdfPhotoImportService(_students_service(db))
    with pytest.raises(ValidationError, match="no existeix"):
        service.parse(tmp_path / "no-existeix.pdf")


def test_parse_rebutja_extensio_incorrecta(db, tmp_path):
    """parse() rebutja un fitxer que no té extensió .pdf."""
    service = PdfPhotoImportService(_students_service(db))
    not_a_pdf = tmp_path / "orla.txt"
    not_a_pdf.write_text("no és un PDF")
    with pytest.raises(ValidationError, match="PDF"):
        service.parse(not_a_pdf)


def test_parse_rebutja_fitxer_corrupte(db, tmp_path):
    """parse() tradueix un PDF corrupte en un error de domini."""
    service = PdfPhotoImportService(_students_service(db))
    corrupt = tmp_path / "orla.pdf"
    corrupt.write_bytes(b"no soc un pdf valid")
    with pytest.raises(ValidationError):
        service.parse(corrupt)


def _students_service(db):
    """Petit embolcall sobre el StudentDAO de prova amb la superfície que cal."""
    from tutopy.services.student_service import StudentService

    return StudentService(
        db.students, db.contacts, db.documents, db.student_group_history,
        db.academic_courses, db.transaction,
    )
