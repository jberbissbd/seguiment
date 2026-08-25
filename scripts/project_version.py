"""Llegeix la versió del projecte declarada a pyproject.toml."""

from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib


PROJECT_FILE = Path(__file__).parents[1] / "pyproject.toml"


def read_project_version(project_file: Path = PROJECT_FILE) -> str:
    """Retorna el valor de `project.version` del fitxer TOML indicat."""
    project = tomllib.loads(project_file.read_text(encoding="utf-8"))
    return project["project"]["version"]


if __name__ == "__main__":
    print(read_project_version())
