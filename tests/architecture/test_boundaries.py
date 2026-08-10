import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "tutopy"


def python_files(path: Path):
    if not path.exists():
        return []
    return sorted(path.rglob("*.py"))


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def forbidden_imports(path: Path, prefixes: tuple[str, ...]) -> list[str]:
    return sorted(
        module for module in imported_modules(path)
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in prefixes)
    )


def test_ui_no_depen_de_negoci_ni_persistencia():
    forbidden = ("tutopy.application", "tutopy.services", "tutopy.database", "sqlite3")
    violations = {
        str(path.relative_to(PROJECT_ROOT)): forbidden_imports(path, forbidden)
        for path in python_files(PACKAGE_ROOT / "ui")
        if forbidden_imports(path, forbidden)
    }
    assert violations == {}


def test_controladors_no_depenen_de_persistencia():
    forbidden = ("tutopy.database", "sqlite3")
    violations = {
        str(path.relative_to(PROJECT_ROOT)): forbidden_imports(path, forbidden)
        for path in python_files(PACKAGE_ROOT / "controllers")
        if forbidden_imports(path, forbidden)
    }
    assert violations == {}


def test_serveis_no_accedeixen_a_la_connexio_sqlite():
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
