"""Proves de la instal·lació d'usuari del llançador Linux."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tutopy.services.desktop_integration import DESKTOP_ID, install_desktop_entry
from tutopy.ui.resources import asset_path


@pytest.mark.parametrize("command", [[], ["tutopy"], ["./Tutopy"]])
def test_rebutja_ordres_sense_executable_absolut(tmp_path, monkeypatch, command):
    """Una ordre invàlida no crea cap recurs d'escriptori."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    icon_source = asset_path("tutopy.svg")
    with pytest.raises(ValueError, match="ruta absoluta"):
        install_desktop_entry(command, icon_source)
    assert list(tmp_path.iterdir()) == []


def test_error_actualitzant_llancador_conserva_anterior_i_neteja_temporal(
    tmp_path, monkeypatch,
):
    """Una fallada en publicar l'actualització no trunca el llançador existent."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    entry = install_desktop_entry(["/opt/Tutopy"], asset_path("tutopy.svg"))
    original = entry.read_bytes()
    replace = Path.replace

    def fail_entry(source, destination):
        if destination == entry:
            raise PermissionError("llançador protegit")
        return replace(source, destination)

    monkeypatch.setattr(Path, "replace", fail_entry)
    icon_source = asset_path("tutopy.svg")
    with pytest.raises(PermissionError, match="protegit"):
        install_desktop_entry(["/opt/Tutopy nou"], icon_source)
    assert entry.read_bytes() == original
    assert list(entry.parent.iterdir()) == [entry]


def test_error_creant_temporal_no_publica_recursos(tmp_path, monkeypatch):
    """La manca de permisos abans d'escriure no deixa una entrada parcial."""
    import tutopy.services.desktop_integration as integration

    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    def denied(**kwargs):
        raise PermissionError("directori protegit")

    monkeypatch.setattr(integration, "NamedTemporaryFile", denied)
    icon_source = asset_path("tutopy.svg")
    with pytest.raises(PermissionError, match="protegit"):
        install_desktop_entry(["/opt/Tutopy"], icon_source)
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_cli_rebutja_instal_lacio_fora_de_linux(monkeypatch, capsys, platform):
    """Una plataforma no compatible retorna un error sense instal·lar res."""
    import tutopy.main as main_module

    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(sys, "argv", ["tutopy", "--install-desktop"])

    def unexpected(*args):
        pytest.fail("No s'ha d'instal·lar el llançador en aquesta plataforma")

    monkeypatch.setattr(main_module, "install_desktop_entry", unexpected)
    assert main_module.main() == 1
    assert "només està disponible a Linux" in capsys.readouterr().err


def test_cli_des_de_fonts_usa_el_mateix_interpret(tmp_path, monkeypatch, capsys):
    """El llançador de desenvolupament conserva l'intèrpret i el mòdul."""
    import tutopy.main as main_module

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(sys, "argv", ["tutopy", "--install-desktop"])
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "entorn virtual/python"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert main_module.main() == 0
    entry = tmp_path / "applications" / f"{DESKTOP_ID}.desktop"
    assert f'Exec="{sys.executable}" "-m" "tutopy.main"' in entry.read_text()
    assert str(entry) in capsys.readouterr().out


@pytest.mark.parametrize("error", [PermissionError("permís denegat"), ValueError("ruta invàlida")])
def test_cli_informa_error_instal_lacio(monkeypatch, capsys, error):
    """Els errors de configuració i escriptura retornen un codi de fallada."""
    import tutopy.main as main_module

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(sys, "argv", ["tutopy", "--install-desktop"])

    def fail(*args):
        raise error

    monkeypatch.setattr(main_module, "install_desktop_entry", fail)
    assert main_module.main() == 1
    captured = capsys.readouterr()
    assert str(error) in captured.err
    assert "Llançador instal·lat" not in captured.out


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
