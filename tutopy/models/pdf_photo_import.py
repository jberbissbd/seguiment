"""Models per a la importació massiva de fotos d'alumnes des d'un PDF "orla"."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PdfPhotoCaption:
    """Etiqueta "N. Cognoms, Nom" llegida d'una cel·la del PDF.

    Attributes:
        num: Número de l'alumne dins de la llista (continu entre pàgines).
        surnames: Cognoms tal com apareixen al PDF.
        name: Nom tal com apareix al PDF.
    """

    num: int
    surnames: str
    name: str

    @property
    def full_name(self) -> str:
        """Retorna el nom complet: ``name`` + ``surnames``."""
        return f"{self.name} {self.surnames}".strip()


@dataclass(frozen=True)
class PdfPhotoEntry:
    """Fotografia extreta del PDF, aparellada amb la seva etiqueta.

    Attributes:
        caption: Etiqueta de l'alumne associada a la fotografia.
        image_path: Ruta del fitxer temporal on s'ha desat la fotografia.
        matched_student_id: Alumne de Tutopy preassignat automàticament per
            coincidència exacta i única de nom, o ``None`` si cal triar-lo
            manualment.
    """

    caption: PdfPhotoCaption
    image_path: str
    matched_student_id: int | None = None


@dataclass(frozen=True)
class PdfPhotoImportPreview:
    """Resultat de l'anàlisi d'un PDF abans d'aplicar cap canvi.

    Attributes:
        entries: Fotografies extretes i aparellades amb la seva etiqueta.
        missing_photos: Etiquetes per a les quals no s'ha trobat cap
            fotografia al PDF (cel·la buida).
        temp_dir: Directori temporal on viuen els fitxers de `entries`;
            s'ha d'eliminar amb :meth:`PdfPhotoImportService.cleanup`.
    """

    entries: tuple[PdfPhotoEntry, ...]
    missing_photos: tuple[PdfPhotoCaption, ...]
    temp_dir: str
