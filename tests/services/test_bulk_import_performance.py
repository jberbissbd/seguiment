from difflib import SequenceMatcher

import pytest

from tutopy.models.messaging import Student
from tutopy.services.bulk_import_service import BulkImportService


def _student(identifier: int, full_name: str) -> Student:
    name, _, surnames = full_name.partition(" ")
    return Student(identifier, f"uuid-{identifier}", name, surnames, "1A")


@pytest.mark.parametrize("threshold", [0.5, 0.86, 0.95, 1.1, 0.0])
def test_index_de_noms_conserva_les_mateixes_coincidencies(threshold):
    names = (
        "julia martinez",
        "julia martines",
        "julieta martinez",
        "joan puig",
        "anna maria serra",
        "x",
        "nom extraordinariament llarg i diferent",
    )
    students = tuple(_student(index, name) for index, name in enumerate(names, 1))
    service = BulkImportService(None, None, None, similarity_threshold=threshold)
    normalized = tuple(zip(students, names))
    index = service._name_index(normalized)

    expected = tuple(
        student for student, name in normalized
        if "julia martines" == name
        or SequenceMatcher(None, "julia martines", name).ratio() >= threshold
    )

    assert service._find_matches("julia martines", index) == expected


def test_index_descarta_longituds_impossibles_abans_de_sequence_matcher(
    monkeypatch,
):
    service = BulkImportService(None, None, None)
    similar = _student(1, "Julia Martines")
    distant = [
        _student(index, "X" * 80 + f" {index}") for index in range(2, 2_002)
    ]
    students = (similar, *distant)
    normalized = tuple(
        (student, service._normalize(student.full_name)) for student in students
    )
    calls = 0
    original = service._similar_names

    def counting_similarity(incoming, current):
        nonlocal calls
        calls += 1
        return original(incoming, current)

    monkeypatch.setattr(service, "_similar_names", counting_similarity)

    matches = service._find_matches("julia martines", service._name_index(normalized))

    assert matches == (similar,)
    assert calls == 1
