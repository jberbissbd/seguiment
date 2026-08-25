"""Utilitats internes per a lectures de relacions per lots."""

from collections.abc import Callable, Iterable
from typing import TypeVar


T = TypeVar("T")
SQLITE_PARAMETER_BATCH = 900


def grouped_by_student(
    connection,
    student_ids: Iterable[int],
    query: str,
    factory: Callable[..., T],
) -> dict[int, list[T]]:
    """Executa una consulta amb ``IN`` per blocs i agrupa els models resultants.

    SQLite limita el nombre de paràmetres (``?``) que admet una sola consulta
    (per defecte 999, vegeu ``SQLITE_PARAMETER_BATCH``). Amb col·leccions grans
    d'identificadors, una clàusula ``IN (...)`` amb un paràmetre per element
    superaria aquest límit, per això la consulta es parteix en blocs de com a
    màxim ``SQLITE_PARAMETER_BATCH`` identificadors i els resultats es
    combinen en un únic diccionari.

    Args:
        connection: Connexió (o ``ManagedConnection``) sobre la qual executar
            la consulta.
        student_ids: Identificadors d'alumnes a cercar; els duplicats
            s'eliminen conservant l'ordre d'aparició.
        query: Plantilla SQL amb un forat ``{placeholders}`` on s'insereix la
            llista de ``?`` del bloc actual.
        factory: Callable (normalment el constructor d'un model) que rep els
            camps d'una fila com a arguments amb nom i retorna l'objecte a
            agrupar; ha d'exposar un atribut ``student_id``.

    Returns:
        Un diccionari ``student_id -> llista d'objectes``, amb una entrada
        (possiblement buida) per a cada identificador demanat.
    """
    unique_ids = tuple(dict.fromkeys(student_ids))
    grouped = {student_id: [] for student_id in unique_ids}
    for offset in range(0, len(unique_ids), SQLITE_PARAMETER_BATCH):
        batch = unique_ids[offset:offset + SQLITE_PARAMETER_BATCH]
        placeholders = ",".join("?" for _ in batch)
        rows = connection.execute(query.format(placeholders=placeholders), batch)
        for row in rows:
            item = factory(**row)
            grouped[item.student_id].append(item)
    return grouped
