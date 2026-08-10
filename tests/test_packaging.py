from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

from scripts.check_release_version import main as check_release_version


ROOT = Path(__file__).parents[1]


def test_release_tag_ha_de_coincidir_amb_pyproject(capsys):
    assert check_release_version("v0.0.1") == 0
    assert check_release_version("v9.9.9") == 1
    assert "no coincideix" in capsys.readouterr().err


def test_release_workflow_construeix_els_tres_sistemes():
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow
    assert "ubuntu-22.04" in workflow
    assert "macos-15-intel" in workflow
    assert "pyinstaller --clean --noconfirm tutopy.spec" in workflow
    assert 'tags:\n      - "v*"' in workflow


def test_spec_es_onefile_i_no_inclou_base_de_dades():
    spec = (ROOT / "tutopy.spec").read_text(encoding="utf-8")
    assert "COLLECT(" not in spec
    assert 'name="Tutopy"' in spec
    assert "seguiment.db" not in spec
    assert "console=False" in spec


def test_versio_de_pyinstaller_esta_fixada():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["optional-dependencies"]["build"]
    assert "pyinstaller==6.21.0" in dependencies
