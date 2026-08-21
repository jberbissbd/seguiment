import pytest

from scripts.performance_baseline import run_baseline


def test_baseline_mesura_operacions_representatives():
    result = run_baseline(student_count=10, note_count=30, repetitions=2)

    assert result["dataset"] == {"students": 10, "notes": 30}
    assert result["repetitions"] == 2
    assert set(result["measurements"]) == {
        "student_search_match",
        "student_search_missing",
        "notes_for_student",
        "notes_content_search",
        "statistics_all",
        "statistics_filtered",
    }
    for measurement in result["measurements"].values():
        assert measurement["min_ms"] <= measurement["median_ms"]
        assert measurement["median_ms"] <= measurement["max_ms"]


@pytest.mark.parametrize(
    ("students", "notes", "repetitions"),
    [(0, 1, 1), (1, -1, 1), (1, 1, 0)],
)
def test_baseline_rebutja_dimensions_invalides(students, notes, repetitions):
    with pytest.raises(ValueError):
        run_baseline(
            student_count=students,
            note_count=notes,
            repetitions=repetitions,
        )
