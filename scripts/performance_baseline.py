"""Genera i mesura una càrrega SQLite representativa de Tutopy."""

from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tutopy.database.database import Database
from tutopy.models.statistics import StatisticsFilters


def _seed(database: Database, student_count: int, note_count: int) -> float:
    started = time.perf_counter()
    connection = database.conn
    with database.transaction():
        connection.executemany(
            "INSERT INTO academic_courses (course) VALUES (?)",
            [("2024-2025",), ("2025-2026",)],
        )
        connection.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [("Acadèmica",), ("Convivència",), ("Família",), ("Orientació",)],
        )
        connection.executemany(
            "INSERT INTO students (uuid, name, surnames, group_name) VALUES (?, ?, ?, ?)",
            (
                (
                    f"00000000-0000-0000-0000-{index:012d}",
                    f"Nom {index:06d}",
                    f"Cognom {student_count - index:06d}",
                    f"{index % 20 + 1:02d}A",
                )
                for index in range(1, student_count + 1)
            ),
        )
        if note_count:
            connection.executemany(
                "INSERT INTO notes "
                "(student_id, category_id, date, course_id, content) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        index % student_count + 1,
                        index % 4 + 1,
                        f"{2024 + index % 2}-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
                        index % 2 + 1,
                        f"Anotació de seguiment {index:07d} "
                        + ("amb incidència" if index % 97 == 0 else "ordinària"),
                    )
                    for index in range(note_count)
                ),
            )
    return time.perf_counter() - started


def _measure(operation: Callable[[], Any], repetitions: int) -> dict[str, float]:
    operation()  # Escalfa la memòria cau de SQLite i la del sistema de fitxers.
    samples = []
    for _ in range(repetitions):
        started = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - started) * 1_000)
    ordered = sorted(samples)
    p95_index = min(len(ordered) - 1, max(0, round(0.95 * len(ordered) - 1)))
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(ordered[p95_index], 3),
        "min_ms": round(ordered[0], 3),
        "max_ms": round(ordered[-1], 3),
    }


def run_baseline(
    *, student_count: int, note_count: int, repetitions: int
) -> dict[str, Any]:
    """Sembra una base de dades temporal i mesura les operacions principals.

    Args:
        student_count: Nombre d'alumnes a generar.
        note_count: Nombre de notes a generar.
        repetitions: Vegades que es repeteix cada operació mesurada, per
            calcular mediana i p95.

    Returns:
        Un diccionari amb el volum de dades, les repeticions, el temps de
        sembra i les mesures (mediana/p95/min/max en ms) per operació.
    """
    if student_count < 1:
        raise ValueError("student_count ha de ser com a mínim 1")
    if note_count < 0:
        raise ValueError("note_count no pot ser negatiu")
    if repetitions < 1:
        raise ValueError("repetitions ha de ser com a mínim 1")

    with tempfile.TemporaryDirectory(prefix="tutopy-performance-") as directory:
        database = Database(str(Path(directory) / "baseline.db")).connect()
        try:
            seed_seconds = _seed(database, student_count, note_count)
            student_id = student_count // 2 + 1
            measurements = {
                "student_search_match": _measure(
                    lambda: database.students.search("Nom 000"), repetitions
                ),
                "student_search_missing": _measure(
                    lambda: database.students.search("inexistent"), repetitions
                ),
                "notes_for_student": _measure(
                    lambda: database.notes.get_by_student(student_id), repetitions
                ),
                "notes_content_search": _measure(
                    lambda: database.notes.get_records({"content": "incidència"}),
                    repetitions,
                ),
                "statistics_all": _measure(
                    lambda: database.statistics.get_snapshot(StatisticsFilters()),
                    repetitions,
                ),
                "statistics_filtered": _measure(
                    lambda: database.statistics.get_snapshot(
                        StatisticsFilters(course_id=1, group_name="01A")
                    ),
                    repetitions,
                ),
            }
        finally:
            database.close()
    return {
        "dataset": {"students": student_count, "notes": note_count},
        "repetitions": repetitions,
        "seed_seconds": round(seed_seconds, 3),
        "measurements": measurements,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--students", type=int, default=1_000)
    parser.add_argument("--notes", type=int, default=10_000)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Emet només JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Executa la línia de comandes: sembra, mesura i imprimeix els resultats."""
    arguments = _parser().parse_args(argv)
    result = run_baseline(
        student_count=arguments.students,
        note_count=arguments.notes,
        repetitions=arguments.repetitions,
    )
    if arguments.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    dataset = result["dataset"]
    print(
        f"Dataset: {dataset['students']} alumnes, {dataset['notes']} anotacions "
        f"(generació: {result['seed_seconds']:.3f} s)"
    )
    print("Operació                         mediana       p95       mín       màx")
    for name, values in result["measurements"].items():
        print(
            f"{name:30} {values['median_ms']:8.3f} "
            f"{values['p95_ms']:9.3f} {values['min_ms']:9.3f} "
            f"{values['max_ms']:9.3f} ms"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
