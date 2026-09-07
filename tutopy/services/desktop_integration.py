"""Instal·lació del llançador i la icona de Tutopy a l'escriptori Linux."""

import os
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile


DESKTOP_ID = "io.github.jberbissbd.Tutopy"


def _exec_argument(value: str) -> str:
    # Exec té dues capes: cometes dels arguments i escapament del valor
    # desktop. Els percentatges literals no han d'esdevenir codis de camp.
    value = value.replace("%", "%%")
    for character in ('\\', '"', '`', '$'):
        value = value.replace(character, "\\" + character)
    value = '"' + value + '"'
    return (value.replace("\\", "\\\\").replace("\n", "\\n")
            .replace("\r", "\\r").replace("\t", "\\t"))


def _write_resource(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install_desktop_entry(command: Sequence[str], icon_source: Path) -> Path:
    """Instal·la un llançador d'usuari i una còpia persistent de la icona.

    Args:
        command: Executable absolut i arguments necessaris per iniciar Tutopy.
        icon_source: SVG inclòs al projecte o al bundle de PyInstaller.

    Returns:
        Ruta del fitxer desktop instal·lat.

    Raises:
        ValueError: Si no es proporciona un executable absolut.
        OSError: Si no es poden llegir o escriure els recursos.
    """
    if not command or not Path(command[0]).is_absolute():
        raise ValueError("Cal indicar una ruta absoluta a l'executable.")
    # GLib comprova si existeix l'executable abans de convertir %% en %.
    # env manté la ruta real com a argument i no implica executar cap shell.
    if "%" in command[0]:
        command = ["/usr/bin/env", "--", *command]
    data_home = Path(os.environ.get("XDG_DATA_HOME", ""))
    if not data_home.is_absolute():
        data_home = Path.home() / ".local" / "share"
    icon_path = data_home / "icons" / "hicolor" / "scalable" / "apps" / f"{DESKTOP_ID}.svg"
    entry_path = data_home / "applications" / f"{DESKTOP_ID}.desktop"
    entry = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Version=1.0\n"
        "Name=Tutopy\n"
        "Comment=Seguiment educatiu de l'alumnat\n"
        f"Exec={' '.join(_exec_argument(argument) for argument in command)}\n"
        f"Icon={DESKTOP_ID}\n"
        "Terminal=false\n"
        "Categories=Education;\n"
        "StartupWMClass=Tutopy\n"
    )
    _write_resource(icon_path, icon_source.read_bytes())
    # Invalida les memòries cau dels temes d'icones després de la instal·lació.
    os.utime(data_home / "icons" / "hicolor", None)
    _write_resource(entry_path, entry.encode("utf-8"))
    return entry_path
