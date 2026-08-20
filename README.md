# Tutopy

Tutopy és una aplicació d'escriptori en català per registrar i consultar el
seguiment educatiu de l'alumnat. Funciona localment: la informació es desa a
l'ordinador de l'usuari i no requereix cap servei web per treballar-hi.

## Funcionalitats

L'aplicació permet:

- crear i gestionar alumnes i grups, també mitjançant edició massiva;
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

## Primers passos

1. Obre **Configuració** i crea les categories que faràs servir per classificar
   les notes.
2. A **Alumnes**, prem **Nou alumne** per crear el primer registre i assignar-li
   un grup.
3. Passa el cursor per sobre d'un alumne i prem el botó rodó **+** que apareix a
   la dreta per afegir-li una nota. El botó també es manté visible a la fila
   seleccionada.
4. Selecciona un alumne per consultar-ne les notes, els descriptors, els
   contactes, els documents i l'històric de grups.

La cerca de la llista permet filtrar per nom, cognoms o grup.

### Edició massiva d'alumnes

Prem **Edició massiva…** a la llista d'alumnes per modificar noms, cognoms o
grups directament en una taula. Per assignar el mateix grup a diverses files:

1. selecciona les files corresponents;
2. escriu o tria el grup;
3. prem **Aplicar grup**;
4. indica la data efectiva del canvi i prem **Aplicar canvis**.

Els canvis de grup s'incorporen a l'històric de cada alumne amb la data
indicada.

### Informes i trimestres

Des de **Configuració → Informes i trimestres** pots ordenar les categories,
seleccionar el logotip dels informes i definir les dates d'inici del segon i
tercer trimestre. La configuració dels trimestres és específica per a cada
combinació de curs acadèmic i grup.

Per exportar un únic informe, selecciona l'alumne i prem **Exportar informe**.
Per generar-ne diversos, utilitza **Exportar diversos…** a la llista.

### Importació i transferència de dades

A **Gestió de dades** pots descarregar la plantilla XLSX i importar alumnes i
categories preparats amb Excel o LibreOffice Calc.

Per traslladar expedients complets entre instal·lacions de Tutopy, exporta els
alumnes seleccionats —o tots els alumnes— en un paquet `.tpy`. El paquet inclou
notes, contactes, descriptors, historial i documents, i queda xifrat amb una
contrasenya d'almenys vuit caràcters. Necessitaràs aquesta mateixa contrasenya
per importar-lo; conserva-la en un lloc segur.

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

Les dades de treball romanen a l'ordinador. Tutopy no necessita enviar-les a
cap servei web. Els paquets `.tpy` són adequats per transferir informació entre
instal·lacions perquè es creen xifrats i se'n comprova la integritat durant la
importació.

## Desenvolupament

El projecte requereix Python 3.10 o superior. Per preparar un entorn de
desenvolupament:

```bash
python -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m ruff check tutopy scripts tests
.venv/bin/python -m pytest
```

A Windows, substitueix `.venv/bin/python` per `.venv\Scripts\python.exe`.

L'aplicació es pot executar amb `.venv/bin/tutopy` o
`.venv/bin/python -m tutopy.main`.

El procés de construcció i publicació està documentat a
[docs/PACKAGING.md](docs/PACKAGING.md).

Els criteris de complexitat, transaccions, SQLite, coalescència d'esdeveniments
i mantenibilitat es documenten a
[docs/ENGINEERING.md](docs/ENGINEERING.md).

El format d'intercanvi entre instàncies i les seves garanties es descriu a
[docs/TRANSFER.md](docs/TRANSFER.md).
