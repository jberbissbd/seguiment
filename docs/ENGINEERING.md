# Criteris d'enginyeria de Tutopy

Aquest document descriu les decisions de rendiment, persistència i mantenibilitat
del projecte. Les estimacions assumeixen `S` alumnes, `N` notes, `D` documents,
`C` categories i `I` files d'una importació.

## Complexitat i límits

### Línia base de rendiment

Abans d'aplicar una optimització, es pot generar una base de dades temporal i
mesurar les operacions principals amb l'entorn virtual del projecte:

```bash
.venv/bin/python scripts/performance_baseline.py \
  --students 1000 --notes 10000 --repetitions 5
```

El script no obre ni modifica la base de dades de l'usuari. També admet
`--json` per conservar els resultats i comparar-los després d'un canvi. Les
mesures són orientatives i s'han de comparar a la mateixa màquina i amb el
mateix volum de dades.

| Operació | Temps | Memòria addicional | Decisió |
| --- | ---: | ---: | --- |
| Llistar o cercar alumnes | `O(S)` | `O(S)` | La cerca conté comodins; es coalescen pulsacions per no repetir-la. |
| Mostrar alumnes | `O(S)` | `O(S)` | Els widgets es reutilitzen si es conserva la seqüència d'identificadors. |
| Filtrar notes | `O(log N + R)` amb índex aplicable | `O(R)` | Els filtres s'executen a SQLite i només es materialitzen els `R` resultats. |
| Estadístiques | `O(N + S)` | `O(S + C)` | Les agregacions es fan a SQLite i no carreguen el text sensible. |
| Generar informes | `O(S + N + C)` | `O(S + N + C)` | El lot comparteix alumnes, notes, cursos, categories i configuració. |
| Transferir alumnes | `O(S + N + D)` | `O(S + N + D)` | Les relacions es carreguen per lots; les lectures SQL no creixen per alumne. |
| Detectar conflictes d'importació | `O(I·S·L²)` pitjor cas | `O(S·L + M)` | La comparació difusa domina; els noms normalitzats es calculen una sola vegada. |

`L` és la longitud del nom i `M` el nombre de coincidències. El límit de 10.000
files evita entrades sense límit. Si les instal·lacions arriben a desenes de
milers d'alumnes, la comparació difusa s'haurà de bloquejar per prefix o tokens;
fer-ho ara podria ocultar coincidències vàlides.

## SQLite, `fsync` i transaccions

Els DAOs poden confirmar una operació autònoma, però `ManagedConnection` suprimeix
els `commit` interns quan un servei obre `Database.transaction()`. Així, una
importació o un canvi coordinat produeix un únic `COMMIT` físic. La capa de servei,
que coneix la unitat de negoci completa, és qui obre la transacció.

Les transaccions niuades creen `SAVEPOINT`. Si una operació interior falla, se'n
desfan només els canvis i la transacció exterior pot capturar l'error i continuar.
Un rollback exterior també desfà els savepoints interiors que ja s'hagin alliberat.

No s'han d'afegir `commit` dins de bucles. Les noves operacions massives han de
seguir aquest patró:

```python
with database.transaction():
    for command in commands:
        service.apply(command)
```

Les claus foranes estan habilitades a cada connexió. L'eliminació d'un alumne
delega les dependències a `ON DELETE CASCADE`; les restriccions `RESTRICT` i
`SET NULL` tampoc s'han de duplicar imperativament.

## Consultes i esquema

Els DAOs projecten columnes explícites. Això evita que afegir una columna trenqui
la construcció dels models i permet que SQLite consideri índexs coberts. Els
índexs segueixen els filtres reals: notes per alumne/curs/categoria/data,
duplicats i historial per alumne o curs. L'índex compost de notes per alumne i
curs evita recórrer totes les notes d'un curs per cada alumne quan es calculen
estadístiques filtrades.

L'esquema es versiona amb `PRAGMA user_version`. Una base nova aplica les
migracions pendents en ordre i la creació de cada versió ha de ser atòmica. Quan
canviï l'esquema, cal incrementar `Database.SCHEMA_VERSION`, afegir un pas nou a
`Database._migrate_schema()` i provar tant una base nova com l'actualització des
de la versió immediatament anterior. L'aplicació rebutja versions d'esquema més
noves que les que coneix per evitar obrir-les de manera incompatible.

Abans d'afegir un índex cal validar la consulta amb `EXPLAIN QUERY PLAN`: cada
índex accelera lectures però encareix escriptures i ocupa disc.

## Esdeveniments i widgets Qt

Les cerques textuals utilitzen `DebouncedLineEdit` (180 ms). Els canvis de
selecció explícits continuen sent immediats. Les estadístiques utilitzen el
mateix principi amb un `QTimer` d'un sol tret.

`StudentList` conserva els widgets quan els identificadors i l'ordre no canvien.
Les notes ajusten el nombre de files i actualitzen els `QTableWidgetItem` existents.
Això és virtualització parcial: redueix assignacions en refrescos, però no evita
el cost lineal de mostrar tots els resultats. Si les llistes creixen molt, el pas
següent és `QAbstractItemModel` amb `QListView`/`QTableView`.

## DRY, errors i documentació

El text compatible amb XML es normalitza a `sanitize_xml_text`, compartit pels
informes DOCX, ODT i PDF. Una nova regla comuna s'ha d'ubicar a la capa més baixa
que no introdueixi dependències inverses.

Els models de domini de `messaging.py` són valors immutables amb `slots`. Els
serveis no han de modificar els objectes rebuts: una normalització o actualització
ha de construir un valor nou (o usar `dataclasses.replace`). Les vistes compostes,
com l'alumne amb contactes i documents, tenen un model de lectura específic en
lloc d'afegir atributs dinàmicament a una entitat.

Es capturen excepcions concretes a les operacions de negoci. Només es permet una
captura genèrica en una frontera externa amb una justificació local, com parsers
de tercers sense jerarquia comuna o neteja que torna a llançar l'excepció original.

Els noms i cognoms passen sempre per `ValidationService.person_name`: s'eliminen
els espais exteriors i les seqüències d'espais, tabulacions o salts es redueixen
a un sol espai. Es conserven capitalització, accents, apòstrofs i guionets. La
representació sense accents i amb `casefold` només s'utilitza per comparar
conflictes d'importació i mai no se substitueix pel valor desat.

El codi públic nou ha d'incloure anotacions de tipus i docstrings segons PEP 257:
resum en imperatiu, línia en blanc abans dels detalls i contractes excepcionals
quan no siguin evidents. Els comentaris expliquen el perquè, no repeteixen el codi.

Ruff és una barrera obligatòria del CI per al codi distribuït. Localment
s'executa amb `python -m ruff check tutopy scripts`; la configuració compartida
és a `pyproject.toml` i exclou la documentació generada o narrativa de `docs`.
