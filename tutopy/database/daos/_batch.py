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
    """Executa una consulta amb ``IN`` per blocs i agrupa els models resultants."""
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
