"""Tests del widget d'esquema de la distribució d'aula."""

from tutopy.models.classroom_layout_generators import generate_columns
from tutopy.ui.widgets.classroom_layout_schematic_widget import AISLE_WEIGHT, _column_weights


def test_column_weights_els_passadissos_valen_la_meitat():
    """Column weights els passadissos valen la meitat."""
    grid = generate_columns("2-2", 4, rows=1)
    weights = _column_weights(grid)
    # "2-2" amb passadís d'una columna: seient, seient, passadís, seient, seient
    assert weights == [1.0, 1.0, AISLE_WEIGHT, 1.0, 1.0]


def test_column_weights_sense_passadissos_tot_val_1():
    """Column weights sense passadissos tot val 1."""
    grid = generate_columns("4", 4, rows=1)
    assert _column_weights(grid) == [1.0, 1.0, 1.0, 1.0]
