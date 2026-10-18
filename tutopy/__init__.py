"""Tutopy: eina d'escriptori per al seguiment educatiu d'alumnes."""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("tutopy")
except PackageNotFoundError:
    # L'executable empaquetat amb PyInstaller no té metadades de
    # distribució instal·lades. En aquest cas, `_frozen_version.py` es
    # genera durant el workflow de release amb la versió real llegida de
    # pyproject.toml, abans d'empaquetar (vegeu .github/workflows/release.yml).
    try:
        from tutopy._frozen_version import __version__
    except ImportError:
        __version__ = "0.0.1"
