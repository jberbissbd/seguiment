"""Proves de la instal·lació d'usuari del llançador Linux."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tutopy.services.desktop_integration import DESKTOP_ID, install_desktop_entry
from tutopy.ui.resources import asset_path


def test_installa_recursos_persistents_i_actualitza_executable(tmp_path, monkeypatch):
    """El desktop apunta al binari real i no a la carpeta temporal del bundle."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "dades"))
    entry = install_desktop_entry(["/opt/Tutopy Linux"], asset_path("tutopy.svg"))
    icon = tmp_path / "dades/icons/hicolor/scalable/apps" / f"{DESKTOP_ID}.svg"
    assert icon.read_bytes() == asset_path("tutopy.svg").read_bytes()
    assert entry.name == f"{DESKTOP_ID}.desktop"
    assert 'Exec="/opt/Tutopy Linux"\n' in entry.read_text()
    assert f"Icon={DESKTOP_ID}\n" in entry.read_text()
    assert "StartupWMClass=Tutopy\n" in entry.read_text()
    install_desktop_entry(["/opt/Tutopy nou"], asset_path("tutopy.svg"))
    assert 'Exec="/opt/Tutopy nou"\n' in entry.read_text()
    assert "_MEI" not in entry.read_text()


def test_xdg_relatiu_utilitza_directori_estandard(tmp_path, monkeypatch):
    """Les rutes XDG relatives no fan dependre el llançador del directori actual."""
    monkeypatch.setenv("XDG_DATA_HOME", "relatiu")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    entry = install_desktop_entry(["/opt/Tutopy"], asset_path("tutopy.svg"))
    assert entry.parent == tmp_path / ".local/share/applications"


@pytest.mark.skipif(sys.platform != "linux", reason="Integració Linux")
def test_installacio_cli_no_arrenca_qt_ni_crea_base_de_dades(tmp_path, monkeypatch):
    """L'ordre també funciona sense servidor gràfic i amb un executable congelat."""
    import tutopy.main as main_module

    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["/opt/Tutopy", "--install-desktop"])
    monkeypatch.setattr(sys, "executable", "/opt/Tutopy")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    def unexpected(*args):
        pytest.fail("La instal·lació no ha d'arrencar Qt ni obrir la base de dades")
    monkeypatch.setattr(main_module, "QApplication", unexpected)
    monkeypatch.setattr(main_module, "Database", unexpected)
    assert main_module.main() == 0
    entry = tmp_path / "applications" / f"{DESKTOP_ID}.desktop"
    assert 'Exec="/opt/Tutopy"\n' in entry.read_text()
    assert not list(tmp_path.rglob("*.db"))


@pytest.mark.skipif(sys.platform != "linux", reason="Integració Linux")
def test_exec_preserva_espais_i_caracters_reservats(tmp_path, monkeypatch):
    """El validador accepta rutes amb espais i caràcters reservats."""
    validator = shutil.which("desktop-file-validate")
    if validator is None:
        pytest.skip("desktop-file-validate no està instal·lat")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    executable = '/opt/amb espais/100% "$dolar" `accent` \\ barra'
    entry = install_desktop_entry([executable], asset_path("tutopy.svg"))
    subprocess.run([validator, str(entry)], check=True, capture_output=True)
    assert "100%%" in entry.read_text()


def test_error_de_lectura_no_publica_llancador(tmp_path, monkeypatch):
    """Un recurs absent no deixa una entrada amb una icona inexistent."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    with pytest.raises(OSError):
        install_desktop_entry(["/opt/Tutopy"], tmp_path / "absent.svg")
    assert not (tmp_path / "applications" / f"{DESKTOP_ID}.desktop").exists()


@pytest.mark.skipif(sys.platform != "linux", reason="Integració Linux")
def test_glib_accepta_executable_amb_percentatge(tmp_path, monkeypatch):
    """GLib pot carregar l'entrada encara que el binari contingui percentatges."""
    python = Path("/usr/bin/python3")
    if not python.is_file():
        pytest.skip("Intèrpret del sistema no disponible")
    probe = subprocess.run(
        [str(python), "-c", "from gi.repository import Gio"],
        capture_output=True, check=False,
    )
    if probe.returncode:
        pytest.skip("Gio no està instal·lat a l'intèrpret del sistema")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "dades"))
    executable = tmp_path / 'Tutopy 100% amb "cometes"'
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    entry = install_desktop_entry([str(executable)], asset_path("tutopy.svg"))
    subprocess.run(
        [str(python), "-c",
         "import sys; from gi.repository import Gio; "
         "assert Gio.DesktopAppInfo.new_from_filename(sys.argv[1]) is not None",
         str(entry)],
        check=True, capture_output=True,
    )
