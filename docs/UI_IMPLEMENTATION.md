# Implementació de la UI de Tutopy

Aquest document descriu l'arquitectura vigent i el pla d'implementació de la
interfície. El codi del repositori és la font de veritat.

## Objectiu

Tutopy és una aplicació local en català per al seguiment educatiu d'alumnes.
La UI permetrà:

- Gestionar alumnes i consultar-ne el detall.
- Registrar i filtrar notes de seguiment.
- Gestionar descriptors generals, contactes i documents.
- Gestionar categories, cursos acadèmics i historials de grup.

## Terminologia del domini

### Nota de seguiment (`Note`)

Registre datat associat a un alumne, una categoria i un curs acadèmic. És
l'entitat que admet filtres per alumne, categoria, curs, dates i contingut.
La seva API pública és `NoteService`.

### Descriptor de l'alumne (`StudentAnnotation`)

Característica general i no datada d'un alumne. No té categoria ni curs
acadèmic. La seva API pública és `AnnotationService`.

La UI no ha d'utilitzar `AnnotationService` per mostrar o filtrar notes de
seguiment.

### Identitat de l'alumne

- `Student.id` és la clau local utilitzada per les relacions SQLite.
- `Student.uuid` és una identitat estable, única i generada internament.
- `StudentNew` no accepta UUID extern.
- Dos alumnes poden compartir nom, cognoms i grup: continuen sent persones
  diferents perquè tenen IDs i UUIDs diferents.
- El nom complet no es pot utilitzar per deduplicar alumnes.

## Arquitectura obligatòria

```text
Usuari
  ↓
UI (widgets i diàlegs)
  ↓ senyals
Controladors
  ↓
Serveis
  ↓
DAOs
  ↓
SQLite
```

### UI

- Mostra dades i recull interaccions.
- Emet senyals i presenta resultats o errors.
- No importa `tutopy.services`, `tutopy.database` ni `tutopy.application`.
- No rep DAOs, connexions ni el contenidor de serveis.
- No conté regles de negoci.

### Controladors

- Connecten els senyals de la UI amb operacions de negoci.
- Reben serveis mitjançant injecció de dependències.
- Transformen valors visuals en models d'entrada.
- Converteixen `DomainError` en missatges en català.
- No importen DAOs, `Database` ni `sqlite3`.

### Serveis

- Són l'única API de negoci disponible per als controladors.
- Implementen CRUD, validació, normalització i regles de negoci.
- Coordinen DAOs i transaccions.
- Retornen models del domini o generen errors de domini.
- No executen SQL ni accedeixen a `.conn`.

Serveis disponibles:

- `StudentService`
- `NoteService`
- `CategoryService`
- `AcademicCourseService`
- `AnnotationService`
- `ContactService`
- `DocumentService`

L'historial de grups queda encapsulat per `StudentService` perquè el canvi de
grup també ha d'actualitzar `students.group_name` dins la mateixa transacció.

### DAOs

- Són l'única capa que conté SQL.
- Persistixen i recuperen models.
- No decideixen regles de negoci.
- Els seus `commit()` respecten les transaccions exteriors gestionades per
  `Database`.

### Composició

`tutopy.application.create_services()` és l'arrel de composició de la capa de
negoci. `tutopy.main` crea la base de dades, el contenidor de serveis, la
finestra i els controladors, als quals injecta els serveis corresponents.

## Estat actual

La base prèvia a la UI està implementada:

- Models i validació estructural.
- Errors de domini.
- Esquema SQLite inicial, claus foranes, restriccions i índexs.
- Transaccions atòmiques per a operacions multi-DAO.
- Serveis necessaris per a la UI.
- Filtres combinables de notes amb lògica AND.
- Composició central de serveis.
- Punt d'entrada Qt i finestra principal mínima.
- Empaquetament instal·lable.

La infraestructura visual de la fase 1 també està implementada:

- Estils globals i paleta inicial.
- Layout principal amb sidebar i navegació entre seccions.
- Llista d'alumnes amb cerca i identitat basada en ID.
- Panell de detall amb les pestanyes previstes.
- Controlador principal connectat a `StudentService`.
- Proves Qt executables en mode offscreen.

La gestió d'alumnes de la fase 2 està implementada:

- Controlador d'alumnes separat del controlador de navegació.
- Creació i edició mitjançant un diàleg validat.
- Edició massiva en taula, amb assignació de grup a les files seleccionades i
  una data efectiva comuna per als canvis d'historial.
- Eliminació amb confirmació explícita.
- Cerca, selecció i actualització dinàmica de la llista.
- Acció contextual per crear una nota des de cada fila, visible amb hover o
  mentre l'alumne està seleccionat.
- Informació bàsica, grup i UUID al panell de detall.
- Canvis de grup sincronitzats amb l'historial.
- Tractament independent d'alumnes homònims.

Les notes de seguiment de la fase 3 estan implementades:

- Taula de notes dins del detall de l'alumne.
- Alta, edició i eliminació amb confirmació.
- Resolució automàtica del curs acadèmic a partir de la data.
- Filtres combinables per alumne, categoria, curs, dates i contingut.
- Selectors d'alumnes que distingeixen homònims mitjançant el UUID.

Les dades complementàries de la fase 4 estan implementades:

- Pestanyes CRUD de descriptors, contactes i documents.
- Historial de grups de només lectura dins del detall de l'alumne.
- Pantalla CRUD de categories.
- Cursos acadèmics derivats i creats automàticament des de les dates.
- Documents copiats a un directori gestionat per Tutopy.
- Controladors connectats exclusivament als serveis de negoci.

El poliment funcional de la fase 5 està implementat:

- Obertura de documents amb l'aplicació predeterminada del sistema.
- Exportació de documents a una ubicació escollida per l'usuari.
- Validació que els fitxers oberts pertanyen al magatzem gestionat.
- Millores visuals i d'estat de botons, taules i seleccions.

## Tecnologies i requisits

- Python 3.10 o superior.
- PySide6 6.11.1.
- SQLite 3.
- pytest i pytest-qt per al desenvolupament.
- UTF-8 i català per a tots els textos visibles.

## Estructura prevista de la UI

```text
tutopy/
├── main.py
├── application.py
├── controllers/
│   ├── main_controller.py
│   ├── student_controller.py
│   ├── note_controller.py
│   ├── catalog_controller.py
│   └── student_related_controller.py
└── ui/
    ├── main_window.py
    ├── styles.py
    ├── widgets/
    │   ├── sidebar.py
    │   ├── student_list.py
    │   ├── student_detail_panel.py
    │   └── crud_views.py
    ├── tabs/
    │   ├── information_tab.py
    │   ├── notes_tab.py
    │   ├── annotation_tab.py
    │   ├── contact_tab.py
    │   ├── document_tab.py
    │   └── history_tab.py
    └── dialogs/
        ├── student_dialog.py
        ├── note_dialog.py
        ├── annotation_dialog.py
        ├── contact_dialog.py
        ├── document_dialog.py
        └── text_value_dialog.py
```

## Fases d'implementació de la UI

### Fase 1: infraestructura visual

Estat: completada.

- [x] Estils globals i paleta.
- [x] Layout de `MainWindow`.
- [x] Sidebar.
- [x] Àrea de llista i detall.
- [x] Controlador principal.
- [x] Proves d'arrencada en mode Qt offscreen.

### Fase 2: alumnes

Estat: completada.

- [x] Llista, cerca i selecció d'alumnes.
- [x] Creació, edició i eliminació mitjançant `StudentService`.
- [x] Edició massiva transaccional amb progrés i cancel·lació.
- [x] Detall bàsic.
- [x] Canvi de grup i sincronització de l'historial.
- [x] Suport correcte d'alumnes homònims.

### Fase 3: notes de seguiment

Estat: completada.

- [x] Taula basada en `NoteService.get_records()`.
- [x] Alta, edició i eliminació.
- [x] Filtres combinables:
  - Categoria.
  - Curs acadèmic.
  - Data inicial i final.
  - Contingut.
- [x] Persistència dels filtres fins que l'usuari els netegi.

### Fase 4: dades complementàries

Estat: completada.

- [x] Descriptors generals.
- [x] Contactes.
- [x] Documents amb emmagatzematge gestionat.
- [x] Historial de grups.
- [x] Categories.
- [x] Cursos acadèmics gestionats automàticament, sense pantalla CRUD.

### Fase 5: poliment i documents

Estat: completada.

- [x] Obertura segura de documents.
- [x] Exportació de documents.
- [x] Estats visuals dels controls desactivats.
- [x] Llegibilitat i selecció de les taules.
- [x] Proves de seguretat de rutes i integració del controlador.

## Convencions visuals

- Framework: Qt Widgets.
- Text visible exclusivament en català.
- Dates internes ISO `YYYY-MM-DD`; format local només a la presentació.
- Navegació per teclat amb Tab, Enter i Escape.
- Confirmació abans d'operacions destructives.
- Errors de domini mostrats amb missatges comprensibles, sense exposar SQL.
- Paths obtinguts mitjançant `tutopy.services.directories`.

Paleta inicial:

```python
PRIMARY_COLOR = "#2B73B7"
SECONDARY_COLOR = "#3D85C6"
ACCENT_COLOR = "#FF6B35"
BACKGROUND_COLOR = "#F5F7FA"
TEXT_PRIMARY = "#2C3E50"
TEXT_SECONDARY = "#7F8C8D"
SUCCESS_COLOR = "#27AE60"
WARNING_COLOR = "#F39C12"
ERROR_COLOR = "#E74C3C"
```

## Execució

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m tutopy.main
```

Després d'una instal·lació també es pot executar amb:

```bash
tutopy
```

## Criteris previs a cada component

Abans d'afegir un widget o controlador:

1. L'operació necessària ha d'existir en un servei.
2. El controlador només ha de rebre serveis i vistes.
3. El widget no ha de conèixer cap servei o DAO.
4. Els errors esperables han de ser `DomainError`.
5. Cal afegir proves del controlador i del comportament visual rellevant.
6. Tota la suite i les comprovacions arquitectòniques han de continuar passant.
