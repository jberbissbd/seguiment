"""Generació d'inicials i colors d'avatar deterministes per alumne.

Deriva, a partir de l'identificador o el nom d'un alumne, unes inicials i
una parella de colors (fons/text) estables perquè el mateix alumne mostri
sempre el mateix avatar arreu de la interfície.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QPixmap

AVATAR_PALETTE = (
    ("#DBEAFE", "#1D4ED8"),
    ("#DCFCE7", "#15803D"),
    ("#FCE7F3", "#BE185D"),
    ("#FEF3C7", "#B45309"),
    ("#EDE9FE", "#6D28D9"),
    ("#CFFAFE", "#0E7490"),
)


def initials(name: str, surnames: str) -> str:
    """Retorna fins a dues inicials en majúscula a partir del nom i cognoms."""
    parts = [part for part in (name.strip(), surnames.strip()) if part]
    return "".join(part[0].upper() for part in parts[:2]) or "?"


def avatar_colors(key: int | str) -> tuple[str, str]:
    """Tria de forma determinista una parella (fons, text) de la paleta.

    Args:
        key: Valor (típicament un ID) a partir del qual es deriva l'índex
            de color, de manera que la mateixa clau doni sempre el mateix
            resultat.

    Returns:
        Una tupla `(color_de_fons, color_de_text)` en format hexadecimal.
    """
    index = sum(ord(character) for character in str(key)) % len(AVATAR_PALETTE)
    return AVATAR_PALETTE[index]


def avatar_stylesheet(key: int | str, radius: int) -> str:
    """Construeix el QSS d'un avatar circular acolorit a partir de `key`.

    Args:
        key: Valor utilitzat per triar el color (vegeu `avatar_colors`).
        radius: Radi de vora, en píxels, per fer-lo circular.
    """
    background, foreground = avatar_colors(key)
    return (
        f"background-color: {background}; color: {foreground}; border: none; "
        f"border-radius: {radius}px; font-weight: 700;"
    )


def circular_pixmap(path: str, size: int) -> QPixmap | None:
    """Carrega una imatge i la retorna retallada en cercle, o `None` si no es pot.

    Escala la imatge mantenint la proporció i en retalla el centre a un
    quadrat de costat `size`, aplicant-hi una màscara circular antialiased.

    Args:
        path: Ruta de la imatge a carregar.
        size: Costat, en píxels, del quadrat final.

    Returns:
        El `QPixmap` circular, o `None` si el fitxer no es pot decodificar
        com a imatge.
    """
    source = QPixmap(path)
    if source.isNull():
        return None
    scaled = source.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (scaled.width() - size) // 2)
    y = max(0, (scaled.height() - size) // 2)
    cropped = scaled.copy(x, y, size, size)

    result = QPixmap(size, size)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path_mask = QPainterPath()
    path_mask.addEllipse(0, 0, size, size)
    painter.setClipPath(path_mask)
    painter.drawPixmap(0, 0, cropped)
    painter.end()
    return result
