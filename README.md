# Tutopy

Tutopy és una aplicació d'escriptori en català per registrar i consultar el
seguiment educatiu de l'alumnat. Funciona localment: la informació es desa a
l'ordinador de l'usuari i no requereix cap servei web per treballar-hi.

## Funcionalitats

L'aplicació permet:

- crear i gestionar alumnes i grups;
- organitzar anotacions de seguiment per categories, cursos acadèmics i
  trimestres;
- mantenir l'històric de grups de cada alumne;
- gestionar contactes, descriptors i documents associats a l'alumnat;
- importar alumnes i categories massivament des d'un full de càlcul;
- exportar informes individuals o de diversos alumnes en format XLSX o DOCX;
- incorporar un logotip comú als informes DOCX;
- exportar, juntament amb els informes, els documents de cada alumne ordenats
  per curs acadèmic.

## Descàrrega

La versió publicada més recent es pot descarregar des de:

**[Descarrega l'última versió de Tutopy](https://github.com/jberbissbd/seguiment/releases/latest)**

A l'apartat **Assets** de la versió, tria el fitxer corresponent al teu sistema:

| Sistema | Fitxer |
| --- | --- |
| Windows de 64 bits | `Tutopy-Windows-x86_64.exe` |
| Linux de 64 bits | `Tutopy-Linux-x86_64` |
| macOS amb processador Intel | `Tutopy-macOS-x86_64` |

El fitxer `SHA256SUMS.txt` permet verificar que les descàrregues no s'han
alterat.

## Com executar el programa

Els fitxers publicats són executables autònoms: no cal instal·lar Python ni les
dependències del projecte.

### Windows

1. Descarrega `Tutopy-Windows-x86_64.exe`.
2. Mou-lo a la carpeta on el vulguis conservar.
3. Executa'l amb un doble clic.

Windows pot mostrar un avís de protecció perquè l'executable encara no està
signat digitalment. Si l'has descarregat des de la pàgina oficial del projecte,
pots revisar l'avís i seleccionar l'opció per executar-lo.

### Linux

1. Descarrega `Tutopy-Linux-x86_64`.
2. Obre un terminal a la carpeta de la descàrrega.
3. Dona-li permís d'execució i inicia'l:

```bash
chmod +x Tutopy-Linux-x86_64
./Tutopy-Linux-x86_64
```

També el pots moure a una carpeta permanent abans d'executar-lo.

### macOS

La versió publicada actualment està construïda per a ordinadors Mac amb
processador Intel (`x86_64`).

1. Descarrega `Tutopy-macOS-x86_64`.
2. Obre el Terminal a la carpeta de la descàrrega.
3. Dona-li permís d'execució i inicia'l:

```bash
chmod +x Tutopy-macOS-x86_64
./Tutopy-macOS-x86_64
```

macOS pot bloquejar la primera execució perquè el binari encara no està signat
ni notaritzat. Si l'has obtingut des de la pàgina oficial, pots autoritzar-lo a
**Configuració del Sistema → Privacitat i seguretat** després del primer intent
d'obertura.

## Dades i actualitzacions

Tutopy desa la base de dades i els documents en la carpeta de dades estàndard
del sistema operatiu, no al costat de l'executable. Per actualitzar el programa:

1. tanca Tutopy;
2. descarrega l'executable de la versió nova;
3. substitueix l'executable anterior o conserva'l amb un altre nom;
4. inicia la versió nova.

Aquest procés no elimina ni trasllada les dades existents. Tot i això, és
recomanable conservar còpies de seguretat periòdiques de la informació
important.

## Desenvolupament

El projecte requereix Python 3.10 o superior. Per preparar un entorn de
desenvolupament:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

L'aplicació es pot executar amb `tutopy` o `python -m tutopy.main`.

El procés de construcció i publicació està documentat a
[docs/PACKAGING.md](docs/PACKAGING.md).
