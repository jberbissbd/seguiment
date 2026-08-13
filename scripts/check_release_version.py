import sys

try:
    from scripts.project_version import read_project_version
except ModuleNotFoundError:  # Execució directa des del directori scripts.
    from project_version import read_project_version


def main(tag: str) -> int:
    version = read_project_version()
    expected_tag = f"v{version}"
    if tag != expected_tag:
        print(f"El tag {tag!r} no coincideix amb la versió {version!r}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
