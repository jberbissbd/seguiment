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

## Pendent abans d'una distribució pública signada

- Afegir icones `.ico`, `.icns` i `.png` al fitxer `tutopy.spec`.
- Configurar Authenticode per a Windows.
- Configurar Developer ID i notarització per a macOS.
- Valorar un build addicional de macOS per Apple Silicon.
