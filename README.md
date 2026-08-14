# Tutopy

Tutopy és una aplicació d'escriptori en català per registrar i consultar el
seguiment educatiu de l'alumnat. Funciona localment: la informació es desa a
l'ordinador de l'usuari i no requereix cap servei web per treballar-hi.

## Funcionalitats

L'aplicació permet:

- crear i gestionar alumnes i grups;
- organitzar anotacions de seguiment per categories, cursos acadèmics i
  trimestres;
- consultar estadístiques de cobertura, evolució temporal i distribució per
  categories sense analitzar el text sensible de les notes;
- mantenir l'històric de grups de cada alumne;
- gestionar contactes, descriptors i documents associats a l'alumnat;
- importar alumnes i categories massivament des de fulls XLSX o ODS;
- exportar informes individuals o de diversos alumnes en format XLSX, DOCX,
  ODT o PDF;
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
| macOS amb Apple Silicon (M1 o posterior) | `Tutopy-macOS-arm64` |

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

Tria l'executable que correspon al processador del Mac:

- `Tutopy-macOS-arm64` per a Apple Silicon (M1, M2, M3, M4 o posterior);
- `Tutopy-macOS-x86_64` per a processadors Intel.

Pots consultar-lo des del menú d'Apple, a **Quant a aquest Mac**.

1. Descarrega l'executable corresponent.
2. Obre el Terminal a la carpeta de la descàrrega.
3. Dona-li permís d'execució i inicia'l:

```bash
chmod +x Tutopy-macOS-arm64
./Tutopy-macOS-arm64
```

Si tens un Mac Intel, substitueix `Tutopy-macOS-arm64` per
`Tutopy-macOS-x86_64` a les dues ordres.

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

Els criteris de complexitat, transaccions, SQLite, coalescència d'esdeveniments
i mantenibilitat es documenten a
[docs/ENGINEERING.md](docs/ENGINEERING.md).

El format d'intercanvi entre instàncies i les seves garanties es descriu a
[docs/TRANSFER.md](docs/TRANSFER.md).
