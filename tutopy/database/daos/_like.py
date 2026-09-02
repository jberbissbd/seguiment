"""Utilitat interna per construir patrons `LIKE` segurs."""


def like_pattern(term: str) -> str:
    """Retorna `term` com a patró `%...%` amb `%`, `_` i `\\` escapats.

    SQLite interpreta `%` i `_` com a comodins dins de `LIKE`. Sense
    escapar-los, una cerca de l'usuari que contingui aquests caràcters (per
    exemple un grup anomenat `1_A`) donaria resultats inesperats. Cal
    combinar el resultat amb la clàusula `ESCAPE '\\'` a la consulta SQL.
    """
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"
