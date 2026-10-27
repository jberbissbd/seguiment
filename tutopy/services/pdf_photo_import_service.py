"""Importació massiva de fotos d'alumnes des d'un PDF "orla" (GICAR/Oracle BI Publisher).

El format sempre és una graella de cel·les amb una fotografia i una
etiqueta "N. Cognoms, Nom" per alumne. És habitual que alguna cel·la no
tingui fotografia, per això les fotos i les etiquetes s'aparellen per
posició de graella (fila/columna) i no per ordre seqüencial: aparellar-les
seqüencialment desquadraria tots els alumnes posteriors a la primera cel·la
buida.
"""

import re
import shutil
import tempfile
import unicodedata
from pathlib import Path

from tutopy.models.pdf_photo_import import (
    PdfPhotoCaption, PdfPhotoEntry, PdfPhotoImportPreview,
)
from tutopy.services.exceptions import ValidationError
from tutopy.services.student_service import StudentService


_NUM_RE = re.compile(r"^(\d+)\.$")


class PdfPhotoImportService:
    """Analitza un PDF "orla" i proposa l'aparellament amb alumnes existents."""

    MAX_FILE_SIZE = 50 * 1024 * 1024
    MAX_PAGES = 50
    GRID_TOLERANCE = 15.0
    MIN_PHOTO_ASPECT_RATIO = 0.85

    def __init__(self, students: StudentService):
        """Injecta el servei d'alumnes, usat per preassignar per coincidència de nom."""
        self.students = students

    def parse(self, source: str | Path) -> PdfPhotoImportPreview:
        """Extreu les fotografies d'un PDF "orla" i les aparella amb el seu peu de foto.

        Args:
            source: Ruta del fitxer PDF a analitzar.

        Returns:
            Les fotografies extretes (amb l'alumne de Tutopy preassignat
            quan el nom coincideix de manera única), les etiquetes sense
            fotografia, i el directori temporal on viuen els fitxers
            extrets (cal eliminar-lo amb :meth:`cleanup`).

        Raises:
            ValidationError: Si el fitxer no existeix, no és un PDF vàlid,
                o supera els límits de mida o nombre de pàgines.
        """
        import pymupdf

        path = Path(source)
        if not path.is_file():
            raise ValidationError("El fitxer PDF seleccionat no existeix.")
        if path.suffix.lower() != ".pdf":
            raise ValidationError("El fitxer ha de ser un PDF.")
        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValidationError("El PDF supera el límit de 50 MB.")
        try:
            doc = pymupdf.open(str(path))
        except Exception as error:
            raise ValidationError("No s’ha pogut obrir el fitxer com a PDF.") from error
        try:
            if doc.page_count > self.MAX_PAGES:
                raise ValidationError(
                    f"El PDF supera el límit de {self.MAX_PAGES} pàgines."
                )
            temp_dir = Path(tempfile.mkdtemp(prefix="tutopy-pdf-photos-"))
            try:
                entries, missing = self._parse_pages(doc, temp_dir)
            except Exception:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise
        finally:
            doc.close()
        matched_entries = self._match_students(entries)
        return PdfPhotoImportPreview(matched_entries, tuple(missing), str(temp_dir))

    def cleanup(self, preview: PdfPhotoImportPreview) -> None:
        """Elimina el directori temporal amb les fotografies extretes."""
        shutil.rmtree(preview.temp_dir, ignore_errors=True)

    def _parse_pages(
        self, doc, temp_dir: Path
    ) -> tuple[list[PdfPhotoEntry], list[PdfPhotoCaption]]:
        entries: list[PdfPhotoEntry] = []
        missing: list[PdfPhotoCaption] = []
        for page in doc:
            photos = self._extract_photo_rects(page)
            captions = self._extract_captions(page)
            pairs, _unmatched_images, page_missing = self._match_grid(photos, captions)
            for photo, caption in sorted(pairs, key=lambda pair: pair[1].num):
                image_path = self._save_photo(doc, photo["xref"], caption.num, temp_dir)
                entries.append(PdfPhotoEntry(caption, str(image_path)))
            missing.extend(page_missing)
        return entries, missing

    def _save_photo(self, doc, xref: int, num: int, temp_dir: Path) -> Path:
        import pymupdf

        pix = pymupdf.Pixmap(doc, xref)
        if pix.n - pix.alpha > 3:  # CMYK o similar -> convertir a RGB
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        destination = temp_dir / f"{num:03d}.jpg"
        pix.save(str(destination))
        return destination

    def _extract_photo_rects(self, page) -> list[dict]:
        """Retorna les imatges dibuixades a la pàgina, descartant el logotip.

        El logotip de capçalera és molt més ample que alt; les fotografies
        d'alumnes són retrats (alçada similar o major que l'amplada).
        """
        photos = []
        for info in page.get_image_info(xrefs=True):
            x0, y0, x1, y1 = info["bbox"]
            width, height = x1 - x0, y1 - y0
            if width <= 0 or height <= 0:
                continue
            if height < width * self.MIN_PHOTO_ASPECT_RATIO:
                continue
            photos.append({"xref": info["xref"], "x0": x0, "y0": y0})
        return photos

    @staticmethod
    def _extract_captions(page) -> list[dict]:
        """Reconstrueix cada etiqueta "N. Cognoms, Nom" a partir de les paraules.

        No depèn del format exacte del bloc de text (els noms llargs
        s'ajusten a diverses línies dins de la mateixa cel·la).
        """
        words = page.get_text("words")
        words.sort(key=lambda word: (word[5], word[6], word[7]))
        captions = []
        current = None

        def close_current():
            if current is not None and current["words"]:
                text = " ".join(current["words"])
                surnames, _, name = text.partition(",")
                captions.append({
                    "caption": PdfPhotoCaption(
                        current["num"], surnames.strip(), name.strip()
                    ),
                    "x0": current["x0"], "y0": current["y0"],
                })

        for x0, y0, _x1, _y1, text, *_rest in words:
            match = _NUM_RE.match(text)
            if match:
                close_current()
                current = {"num": int(match.group(1)), "x0": x0, "y0": y0, "words": []}
            elif current is not None:
                current["words"].append(text)
        close_current()
        return captions

    def _match_grid(self, photos: list[dict], captions: list[dict]):
        """Aparella fotos i etiquetes per coordenades de graella (fila, columna).

        Agrupa per separat les coordenades X/Y de les fotos i de les
        etiquetes, de manera que una cel·la sense fotografia no desquadri
        l'aparellament de la resta.
        """
        tol = self.GRID_TOLERANCE
        img_cols = self._cluster([photo["x0"] for photo in photos], tol)
        img_rows = self._cluster([photo["y0"] for photo in photos], tol)
        txt_cols = self._cluster([item["x0"] for item in captions], tol)
        txt_rows = self._cluster([item["y0"] for item in captions], tol)

        caption_by_cell = {}
        for item in captions:
            cell = (
                self._nearest_index(item["y0"], txt_rows),
                self._nearest_index(item["x0"], txt_cols),
            )
            caption_by_cell[cell] = item["caption"]

        pairs = []
        unmatched_images = []
        for photo in photos:
            cell = (
                self._nearest_index(photo["y0"], img_rows),
                self._nearest_index(photo["x0"], img_cols),
            )
            caption = caption_by_cell.get(cell)
            if caption is None:
                unmatched_images.append(photo)
            else:
                pairs.append((photo, caption))

        matched_nums = {caption.num for _photo, caption in pairs}
        missing = [
            item["caption"] for item in captions if item["caption"].num not in matched_nums
        ]
        return pairs, unmatched_images, missing

    @staticmethod
    def _cluster(values: list[float], tol: float) -> list[float]:
        """Agrupa coordenades properes en "clústers" (columnes o files)."""
        if not values:
            return []
        ordered = sorted(values)
        clusters = [[ordered[0]]]
        for value in ordered[1:]:
            if value - clusters[-1][-1] <= tol:
                clusters[-1].append(value)
            else:
                clusters.append([value])
        return [sum(cluster) / len(cluster) for cluster in clusters]

    @staticmethod
    def _nearest_index(value: float, centers: list[float]) -> int:
        """Índex (0-based) del centre de clúster més proper a `value`."""
        return min(range(len(centers)), key=lambda index: abs(centers[index] - value))

    def _match_students(self, entries: list[PdfPhotoEntry]) -> tuple[PdfPhotoEntry, ...]:
        """Preassigna cada entrada a l'alumne existent amb nom normalitzat únic."""
        students_by_name: dict[str, list] = {}
        for student in self.students.get_all():
            key = self._normalize(student.filing_name)
            students_by_name.setdefault(key, []).append(student)
        matched = []
        for entry in entries:
            key = self._normalize(f"{entry.caption.surnames}, {entry.caption.name}")
            candidates = students_by_name.get(key, ())
            student_id = candidates[0].id if len(candidates) == 1 else None
            matched.append(PdfPhotoEntry(entry.caption, entry.image_path, student_id))
        return tuple(matched)

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalitza un nom per comparar-lo sense accents, majúscules ni espais extra."""
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())
