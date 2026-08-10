# Tutopy

Aplicació local en català per al seguiment educatiu d'alumnes.

## Desenvolupament

Requereix Python 3.10 o superior.

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

L'aplicació es pot executar amb `tutopy` o `python -m tutopy.main`.

## Releases

Els executables `onefile` per a Windows, Linux i macOS es construeixen amb
GitHub Actions quan es publica un tag que coincideix amb la versió de
`pyproject.toml`. Consulta [docs/PACKAGING.md](docs/PACKAGING.md) per al procés
complet.
