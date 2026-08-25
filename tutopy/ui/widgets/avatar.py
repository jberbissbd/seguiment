"""Generació d'inicials i colors d'avatar deterministes per alumne.

Deriva, a partir de l'identificador o el nom d'un alumne, unes inicials i
una parella de colors (fons/text) estables perquè el mateix alumne mostri
sempre el mateix avatar arreu de la interfície.
"""

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
