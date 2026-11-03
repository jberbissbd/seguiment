"""Verifica els límits arquitectònics entre capes (ui/controladors/serveis/database)."""

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "tutopy"


def python_files(path: Path):
    """Retorna els fitxers `.py` de `path`, o una llista buida si no existeix."""
    if not path.exists():
        return []
    return sorted(path.rglob("*.py"))


def imported_modules(path: Path) -> set[str]:
    """Retorna els noms de mòdul importats pel fitxer `path`."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def forbidden_imports(path: Path, prefixes: tuple[str, ...]) -> list[str]:
    """Retorna els mòduls importats per `path` que comencen per algun de `prefixes`."""
    return sorted(
        module for module in imported_modules(path)
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in prefixes)
    )


def test_ui_no_depen_de_negoci_ni_persistencia():
    """Ui no depen de negoci ni persistència."""
    forbidden = ("tutopy.application", "tutopy.services", "tutopy.database", "sqlite3")
    violations = {
        str(path.relative_to(PROJECT_ROOT)): forbidden_imports(path, forbidden)
        for path in python_files(PACKAGE_ROOT / "ui")
        if forbidden_imports(path, forbidden)
    }
    assert violations == {}


def test_controladors_no_depenen_de_persistencia():
    """Controladors no depenen de persistència."""
    forbidden = ("tutopy.database", "sqlite3")
    violations = {
        str(path.relative_to(PROJECT_ROOT)): forbidden_imports(path, forbidden)
        for path in python_files(PACKAGE_ROOT / "controllers")
        if forbidden_imports(path, forbidden)
    }
    assert violations == {}


def test_serveis_no_accedeixen_a_la_connexio_sqlite():
    """Serveis no accedeixen a la connexió sqlite."""
    violations = []
    for path in python_files(PACKAGE_ROOT / "services"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = imported_modules(path)
        accesses_conn = any(
            isinstance(node, ast.Attribute) and node.attr == "conn"
            for node in ast.walk(tree)
        )
        if "sqlite3" in imports or accesses_conn:
            violations.append(str(path.relative_to(PROJECT_ROOT)))
    assert violations == []
