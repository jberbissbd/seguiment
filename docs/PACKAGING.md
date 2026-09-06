# Empaquetament i releases

Tutopy es construeix amb PyInstaller en mode `onefile`. Els binaris no es
generen localment per publicar-los: el workflow `release.yml` crea cada
artefacte al sistema operatiu de destinació.

## Publicar una versió

1. Actualitza `project.version` a `pyproject.toml`.
2. Executa les proves i integra els canvis a la branca principal.
3. Crea i envia un tag coincident, per exemple `v0.1.0`.
4. GitHub Actions valida la versió, executa les proves i construeix Windows,
   Linux i macOS, amb executables natius per a Intel i Apple Silicon en aquest
   últim sistema.
5. Si tots els jobs passen, es crea una GitHub Release amb els executables i
   `SHA256SUMS.txt`.

Els tags que no coincideixen exactament amb `pyproject.toml` fallen abans de
construir. `workflow_dispatch` permet provar els builds manualment, però no
publica cap release perquè no s'executa sobre un tag.

## Dades persistents

La base de dades i els documents no formen part de l'executable. Es desen sota
el directori de dades estàndard de cada sistema dins d'una carpeta estable
`Tutopy`. Moure o substituir l'executable no mou ni elimina les dades.

## Icona i llançador de Linux

L'opció `icon` de PyInstaller no afegeix una icona als executables ELF.
La finestra continua rebent la icona amb `setWindowIcon`, i
`setDesktopFileName("io.github.jberbissbd.Tutopy")` identifica l'entrada que
l'escriptori ha d'associar a l'aplicació.

El binari Linux inclou l'ordre `--install-desktop`, que escriu:

- `$XDG_DATA_HOME/applications/io.github.jberbissbd.Tutopy.desktop`;
- `$XDG_DATA_HOME/icons/hicolor/scalable/apps/io.github.jberbissbd.Tutopy.svg`.

Si `XDG_DATA_HOME` no és una ruta absoluta, utilitza `~/.local/share`.
La icona es copia fora de `_MEIPASS` i el camp `Exec` apunta a
`sys.executable`, amb escapament de les rutes amb espais i caràcters especials.
L'ordre no arrenca Qt ni obre la base de dades. Cal repetir-la si es mou el binari.
En executar-la des del codi font, el llançador utilitza el mateix intèrpret amb
`-m tutopy.main`; el projecte ha d'estar instal·lat en aquell entorn.

La icona pròpia al gestor de fitxers correspon al llançador `.desktop`; el
binari descarregat pot conservar la icona genèrica. La representació al dock
s'ha de validar en un escriptori Linux real, tant amb X11 com amb Wayland.

Referències: [identitat d'escriptori a Qt](https://doc.qt.io/qt-6/qguiapplication.html#desktopFileName-prop),
[opcions de PyInstaller](https://pyinstaller.org/en/stable/usage.html),
[format del camp Exec](https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html).

## Pendent abans d'una distribució pública signada

- Afegir icones `.ico`, `.icns` i `.png` al fitxer `tutopy.spec`.
- Configurar Authenticode per a Windows.
- Configurar Developer ID i notarització per a macOS.
- Valorar un build addicional de macOS per Apple Silicon.
