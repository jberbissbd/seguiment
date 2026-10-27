"""Codificació MIME de l'arrossegament d'alumnes al pla de distribució d'aula.

L'origen (`"pending"` o `"cell:{row}:{column}"`) viatja amb l'alumne perquè
qui rep el `drop` sàpiga si cal intercanviar dues cel·les o simplement
treure l'alumne de la llista de pendents.
"""

from PySide6.QtCore import QMimeData

MIME_TYPE = "application/x-tutopy-student"
PENDING_ORIGIN = "pending"


def encode(student_id: int, origin: str) -> QMimeData:
    """Codifica l'alumne arrossegat i el seu origen en un `QMimeData`."""
    mime_data = QMimeData()
    mime_data.setData(MIME_TYPE, f"{student_id}:{origin}".encode("utf-8"))
    return mime_data


def decode(mime_data: QMimeData) -> tuple[int, str] | None:
    """Decodifica `(student_id, origin)` d'un `QMimeData`, o `None` si no és vàlid."""
    if not mime_data.hasFormat(MIME_TYPE):
        return None
    try:
        text = bytes(mime_data.data(MIME_TYPE)).decode("utf-8")
        student_id_text, origin = text.split(":", 1)
        return int(student_id_text), origin
    except (ValueError, UnicodeDecodeError):
        return None


def cell_origin(row: int, column: int) -> str:
    """Retorna l'identificador d'origen d'una cel·la `(row, column)`."""
    return f"cell:{row}:{column}"


def parse_cell_origin(origin: str) -> tuple[int, int] | None:
    """Retorna `(row, column)` si `origin` és una cel·la, o `None` si és pendents."""
    if not origin.startswith("cell:"):
        return None
    try:
        _, row_text, column_text = origin.split(":", 2)
        return int(row_text), int(column_text)
    except ValueError:
        return None
