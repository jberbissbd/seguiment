# Criteris d'enginyeria de Tutopy

Aquest document descriu les decisions de rendiment, persistència i mantenibilitat
del projecte. Les estimacions assumeixen `S` alumnes, `N` notes, `D` documents,
`C` categories i `I` files d'una importació.

## Complexitat i límits

| Operació | Temps | Memòria addicional | Decisió |
| --- | ---: | ---: | --- |
| Llistar o cercar alumnes | `O(S)` | `O(S)` | La cerca conté comodins; es coalescen pulsacions per no repetir-la. |
| Mostrar alumnes | `O(S)` | `O(S)` | Els widgets es reutilitzen si es conserva la seqüència d'identificadors. |
| Filtrar notes | `O(log N + R)` amb índex aplicable | `O(R)` | Els filtres s'executen a SQLite i només es materialitzen els `R` resultats. |
| Estadístiques | `O(N + S)` | `O(S + C)` | Les agregacions es fan a SQLite i no carreguen el text sensible. |
| Generar un informe | `O(N + C)` | `O(N + C)` | Cursos i categories es precomputen una vegada per exportació. |
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
duplicats i historial per alumne o curs.

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
