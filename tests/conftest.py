"""Configuració i classificació comuna de tota la suite."""

import os
import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_collection_modifyitems(items):
    """Permet seleccionar la suite amb ``-m unit|integration|ui``."""
    for item in items:
        if any(item.get_closest_marker(name) for name in ("unit", "integration", "ui")):
            continue
        path = item.path.as_posix()
        if "/tests/ui/" in path:
            marker = pytest.mark.ui
        elif any(part in path for part in (
            "/tests/database/", "/tests/services/", "/tests/controllers/",
        )):
            marker = pytest.mark.integration
        else:
            marker = pytest.mark.unit
        item.add_marker(marker)
