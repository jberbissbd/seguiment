# Implementació de la UI - Seguiment d'Alumnes

## Taula de Continguts

1. [Visió General](#visió-general)
2. [Arquitectura](#arquitectura)
3. [Tecnologies](#tecnologies)
4. [Estructura de Fitxers](#estructura-de-fitxers)
5. [Fases d'Implementació](#fases-dimplementació)
6. [Components Principals](#components-principals)
7. [Estils i Aparença](#estils-i-aparença)
8. [Consideracions Cross-Plataforma](#consideracions-cross-plataforma)
9. [Requisits de Text](#requisits-de-text)
10. [Filtres d'Anotacions](#filtres-dannotacions)

---

## Visió General

Aplicació de seguiment d'alumnes amb interfície gràfica que permet:
- Visualitzar llistat d'alumnes
- Consultar detalls de cada alumne
- Afegir, editar i eliminar anotacions/notes de seguiment
- Filtrar anotacions per diferents paràmetres (combinables)
- Gestionar categories i cursos acadèmics

---

## Arquitectura

Model-View-Controller (MVC) adaptat per Qt:

```
User → View (Widgets) → Controller → Service → DAO → Database
                ↑                     ↑
           (Signals)            (Data Models)
```

### Flux de Dades

1. **View**: Recol·leixa events d'usuari (clics, seleccions, entrada de text)
2. **Controller**: Processa events i invoca serveis
3. **Service**: Lògica de negoci, transformació de dades
4. **DAO**: Accés a base de dades (SQLite)
5. **Database**: Persistència

### Separació de Responsabilitats

- **Widgets (View)**: Només UI, sense lògica de negoci
- **Controllers**: Mediador entre View i Service
- **Services**: Operacions CRUD i regles de negoci
- **DAOs**: Consultes SQL i mapeig a models

---

## Tecnologies

- **UI Framework**: PySide6 (Qt for Python)
- **Base de Dades**: SQLite 3
- **Testing**: pytest
- **Llengua**: Català (UTF-8)
- **Sistema Operatiu**: Cross-plataforma (Windows, macOS, Linux)

---

## Estructura de Fitxers

```
tutopy/
├── main.py                          # Punt d'entrada de l'aplicació
├── models/
│   └── messaging.py                 # Data classes (Student, Note, Category, etc.)
├── services/
│   ├── __init__.py
│   ├── directories.py              # Gestió de paths (ja implementat)
│   ├── student_service.py          # Lògica de negoci: alumnes
│   ├── annotation_service.py       # Lògica de negoci: anotacions
│   ├── category_service.py         # Lògica de negoci: categories
│   ├── academic_course_service.py  # Lògica de negoci: cursos
│   ├── note_service.py             # Lògica de negoci: notes
│   ├── validation_service.py       # Validació de dades
│   └── utils.py                     # Utilitats
├── database/
│   ├── __init__.py
│   ├── database.py                 # Connexió i inicialització DB
│   └── daos/
│       ├── __init__.py
│       ├── student_dao.py          # Accés a dades: alumnes
│       ├── annotation_dao.py       # Accés a dades: anotacions
│       ├── category_dao.py         # Accés a dades: categories
│       ├── academic_course_dao.py  # Accés a dades: cursos
│       └── ...
├── controllers/
│   ├── __init__.py
│   ├── student_controller.py       # Controlador: alumnes
│   ├── annotation_controller.py    # Controlador: anotacions
│   └── main_controller.py          # Controlador principal
└── ui/
    ├── __init__.py
    ├── styles.py                   # CSS global i colors
    ├── main_window.py              # Finestra principal
    ├── widgets/
    │   ├── __init__.py
    │   ├── sidebar.py              # Navegació lateral
    │   ├── student_list.py          # Llista d'alumnes
    │   ├── student_list_item.py     # Item individual de llista
    │   ├── student_detail_panel.py  # Panell de detalls amb pestanyes
    │   ├── annotation_filter.py     # Filtres combinables
    │   └── ...
    ├── tabs/
    │   ├── __init__.py
    │   ├── annotations_tab.py       # Pestanya d'anotacions
    │   ├── notes_tab.py            # Pestanya de notes
    │   ├── contacts_tab.py          # Pestanya de contactes
    │   └── documents_tab.py         # Pestanya de documents
    └── dialogs/
        ├── __init__.py
        ├── student_dialog.py        # Diàleg creació/edició alumne
        ├── annotation_dialog.py     # Diàleg creació/edició anotació
        └── ...
```

---

## Fases d'Implementació

### Fase 1: Infraestructura Base (Prioritat Alta)

**Objectiu**: Establir la base de la UI sense funcionalitat complexa

#### Tasques:
1. ✅ Configuració de PySide6 i HighDPI
2. ✅ Estructura de directoris
3. ✅ Estils globals (CSS) amb colors definits
4. ✅ Finestra principal (MainWindow) amb layout base
5. ✅ Sidebar de navegació
6. ✅ Llista d'alumnes (bàsica)
7. ✅ Panell de detalls amb pestanyes
8. ✅ Widget de filtres d'anotacions
9. ✅ Diàlegs bàsics (student, annotation)
10. ✅ Controladors bàsics

#### Criteris d'acceptació:
- La UI s'inicia sense errors
- Tots els widgets són visibles i accesibles
- L'estil és consistent en totes les plataformes
- El text està en català amb codificació UTF-8

---

### Fase 2: Gestió d'Alumnes (Prioritat Alta)

**Objectiu**: Implementar CRUD complet d'alumnes

#### Tasques:
1. Controlador d'alumnes amb connexió a StudentService
2. Llista d'alumnes amb selecció i doble clic
3. Diàleg d'alumne amb validació
4. Actualització dinàmica de la llista
5. Visualització de detalls bàsics

---

### Fase 3: Anotacions i Filtres (Prioritat Alta)

**Objectiu**: Implementar el visor d'anotacions amb filtres

#### Tasques:
1. Pestanya d'anotacions amb taula
2. Filtres per:
   - Alumne
   - Categoria
   - Curs acadèmic
   - Data (rang)
   - Text de contingut
3. Lògica AND per a filtres combinats
4. Diàleg d'anotació
5. Connexió amb AnnotationService

---

### Fase 4: Funcionalitats Addicionals (Prioritat Mitjana)

**Objectiu**: Completa la UI amb les restants funcionalitats

#### Tasques:
1. Pestanya de notes
2. Pestanya de contactes
3. Pestanya de documents
4. Pestanya d'històric de grups
5. Menú superior amb opcions
6. Accions de/uix (exportar, estadístiques, etc.) - *Fora d'abast inicial*

---

## Components Principals

### 1. MainWindow (`ui/main_window.py`)

Finestra principal amb:
- **Sidebar**: Navegació entre seccions (Alumnes, Categories, Cursos, Estadístiques)
- **Contingut Central**: Àrea de treball principal
  - Llista d'alumnes (esquerra)
  - Panell de detalls (dreta)
- **Barra d'estat**: Missatges i informació

Layout:
```
┌─────────────────────────────────────────────────────────┐
│   Títol de l'Aplicació                     [Menú]         │
├─────────────┬────────────────────────────────────────────┤
│             │                                                        │
│  SIDEBAR    │   LLISTA          │   PANELL           │
│  (200px)    │   ALUMNES         │   DETALLS          │
│             │   (flexible)      │   (flexible)       │
│             │                                                        │
├─────────────┴────────────────────────────────────────────┤
│  Barra d'estat                                              │
└─────────────────────────────────────────────────────────┘
```

### 2. Sidebar (`ui/widgets/sidebar.py`)

- Botons per a cada secció
- Icones + Text
- Estil consistent amb la temàtica
- Selecció visual clar

Seccions:
- 📚 Alumnes (secció principal)
- 🏷️ Categories
- 📅 Cursos Acadèmics
- 📊 Estadístiques (futur)
- ⚙️ Configuració (futur)

### 3. StudentList (`ui/widgets/student_list.py`)

- QListWidget o QTableWidget
- Mostra: Nom complet, grup, indicadors
- Ordenació per nom, grup, data de creació
- Busqueda ràpida (filter)
- Selecció única
- Doble clic: editar alumne

### 4. StudentDetailPanel (`ui/widgets/student_detail_panel.py`)

Panell amb pestanyes:
- **Informació**: Dades bàsiques de l'alumne
- **Anotacions**: Llista d'anotacions amb filtres
- **Notes**: Notes de seguiment
- **Contactes**: Persones de contacte
- **Documents**: Documents adjunts
- **Històric**: Històric de grups

### 5. AnnotationFilter (`ui/widgets/annotation_filter.py`)

Filtres combinables amb lògica AND:
- Selector d'alumne (ComboBox)
- Selector de categoria (ComboBox)
- Selector de curs acadèmic (ComboBox)
- Rang de dates (QDateEdit)
- Camp de text (contingut)
- Botó "Filtrar" i "Netejar"

### 6. Diàlegs

- **StudentDialog**: Crear/editar alumne
  - Camps: Nom, Cognoms, Grup
  - Validació: camps obligatoris
  - UUID generat automàticament

- **AnnotationDialog**: Crear/editar anotació
  - Camps: Alumne (read-only si ve de context), Categoria, Data, Curs, Contingut
  - Validació: Alumne, Categoria, Contingut obligatoris

- **CategoryDialog**: Crear/editar categoria
- **AcademicCourseDialog**: Crear/editar curs

---

## Estils i Aparença

### Colors Principals (definits a `ui/styles.py`)

```python
PRIMARY_COLOR = "#2B73B7"      # Blau corporatiu
SECONDARY_COLOR = "#3D85C6"    # Blau secundari
ACENT_COLOR = "#FF6B35"         # Taronja accent
BACKGROUND_COLOR = "#F5F7FA"   # Gris clar fons
TEXT_PRIMARY = "#2C3E50"       # Text principal
TEXT_SECONDARY = "#7F8C8D"     # Text secundari
SUCCESS_COLOR = "#27AE60"      # Verd èxit
WARNING_COLOR = "#F39C12"      # Groc advertència
ERROR_COLOR = "#E74C3C"        # Vermell error
```

### CSS Global

```python
MAIN_CSS = """
QMainWindow {
    background-color: #F5F7FA;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
}

QPushButton {
    background-color: PRIMARY_COLOR;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-height: 36px;
}

QPushButton:hover {
    background-color: SECONDARY_COLOR;
}

QPushButton:disabled {
    background-color: #BDC3C7;
}

QLineEdit, QComboBox, QDateEdit, QPlainTextEdit {
    border: 1px solid #BDC3C7;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
    selection-background-color: PRIMARY_COLOR;
}

QTableWidget, QListWidget {
    border: 1px solid #BDC3C7;
    border-radius: 4px;
    background-color: white;
    alternate-background-color: #ECF0F1;
}

QHeaderView::section {
    background-color: PRIMARY_COLOR;
    color: white;
    padding: 8px;
    border: none;
}

QTabWidget::pane {
    border: 1px solid #BDC3C7;
    border-radius: 4px;
    background-color: white;
}

QTabWidget::tab-bar {
    left: 5px;
}

QTabBar::tab {
    background-color: #ECF0F1;
    border: 1px solid #BDC3C7;
    border-radius: 4px 4px 0 0;
    padding: 8px 16px;
    color: TEXT_PRIMARY;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom-color: white;
    color: PRIMARY_COLOR;
}

QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: #ECF0F1;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle {
    background: #BDC3C7;
    border-radius: 5px;
}

QScrollBar::handle:hover {
    background: #95A5A6;
}

QStatusBar {
    background-color: PRIMARY_COLOR;
    color: white;
}
"""
```

### Configuració HighDPI

```python
# A main.py, abans de crear QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

# Enable HighDPI scaling
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

---

## Consideracions Cross-Plataforma

### 1. Paths i Fitxers
- Utilitzar `services/directories.py` per obtenir paths
- `get_project_root()` per l'arrel del projecte en desenvolupament
- `get_app_data_dir()` per dades persistents
- `get_db_path()` per la base de dades
- Evitar paths absoluts

### 2. Estils i Fonts
- Fonts definides com a familia genèrica: `'Segoe UI', 'Arial', sans-serif`
- Mides en px (Qt gestiona l'escalat)
- Colors en hexadecimal
- CSS consistent en totes les plataformes

### 3. Comportament
- Navegació amb teclat (Tab, Enter, Escape)
- Accelaradors de teclat consistent
- Ordenació de taules respectant locale
- Dates en format ISO (YYYY-MM-DD) internament, format local a UI

### 4. Qt-Specific
- `QGuiApplication.setHighDpiScaleFactorRoundingPolicy()` per HighDPI
- `QtCore.Qt.AA_EnableHighDpiScaling` i `QtCore.Qt.AA_UseHighDpiPixmaps`
- Icones en SVG per escalat perfecte

---

## Requisits de Text

### Codificació
- **UTF-8** en tots els fitxers
- **Català** en totes les etiquetes, missatges i contingut
- Validació de text en models (messaging.py)

### Exemples de Text

```python
# Etiquetes
"Nom:" -> "Nom:"
"Surname:" -> "Cognoms:"
"Group:" -> "Grup:"
"Category:" -> "Categoria:"
"Date:" -> "Data:"
"Content:" -> "Contingut:"
"Search:" -> "Cercar:"
"Filter:" -> "Filtrar"
"Clear:" -> "Netejar"
"Save:" -> "Desar"
"Cancel:" -> "Cancel·lar"
"New:" -> "Nou"
"Edit:" -> "Editar"
"Delete:" -> "Eliminar"

# Missatges
"Student created successfully" -> "Alumne creat correctament"
"Error deleting student" -> "Error en eliminar l'alumne"
"Are you sure?" -> "Estàs segur?"

# Pestanyes
"Information" -> "Informació"
"Annotations" -> "Anotacions"
"Notes" -> "Notes"
"Contacts" -> "Contactes"
"Documents" -> "Documents"
"History" -> "Històric"
```

### Base de Dades
- Les anotacions guardades a la BD han de mantindre la codificació UTF-8
- Usar paràmetres en consultes SQL per evitar problemes d'encodatge
- SQLite gestiona UTF-8 per defecte

---

## Filtres d'Anotacions

### Requisits
- Filtrar per qualsevol camp individualment
- Filtrar per combinació de camps (lògica AND)
- Filtres persistents fins que es netegin
- Actualització automàtica de resultats

### Implementació

```python
# A annotation_controller.py
class AnnotationController:
    def filter_annotations(self, filters: dict) -> list[Annotation]:
        """
        Filtres acceptats:
        - student_id: int | None
        - category_id: int | None
        - course_id: int | None
        - date_from: str (YYYY-MM-DD) | None
        - date_to: str (YYYY-MM-DD) | None
        - content: str | None
        """
        result = self.annotation_service.get_all()
        
        if filters.get('student_id'):
            result = [a for a in result if a.student_id == filters['student_id']]
        if filters.get('category_id'):
            result = [a for a in result if a.category_id == filters['category_id']]
        if filters.get('course_id'):
            result = [a for a in result if a.course_id == filters['course_id']]
        if filters.get('date_from'):
            result = [a for a in result if a.date >= filters['date_from']]
        if filters.get('date_to'):
            result = [a for a in result if a.date <= filters['date_to']]
        if filters.get('content'):
            result = [a for a in result 
                     if filters['content'].lower() in a.content.lower()]
        
        return result
```

### Widget de Filtres

```python
# A ui/widgets/annotation_filter.py
class AnnotationFilter(QWidget):
    filter_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Filtre per alumne
        self.student_combo = QComboBox()
        layout.addRow("Alumne:", self.student_combo)
        
        # Filtre per categoria
        self.category_combo = QComboBox()
        layout.addRow("Categoria:", self.category_combo)
        
        # Filtre per curs
        self.course_combo = QComboBox()
        layout.addRow("Curs acadèmic:", self.course_combo)
        
        # Filtre per data
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        layout.addRow("Data (des de):", self.date_from)
        layout.addRow("Data (fins a):", self.date_to)
        
        # Filtre per contingut
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("Cercar en contingut...")
        layout.addRow("Contingut:", self.content_edit)
        
        # Botons
        btn_layout = QHBoxLayout()
        self.filter_btn = QPushButton("Filtrar")
        self.clear_btn = QPushButton("Netejar")
        btn_layout.addWidget(self.filter_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addRow(btn_layout)
    
    def connect_signals(self):
        self.filter_btn.clicked.connect(self.apply_filter)
        self.clear_btn.clicked.connect(self.clear_filter)
        self.content_edit.textChanged.connect(self.delayed_filter)
    
    def get_filters(self) -> dict:
        return {
            'student_id': self.student_combo.currentData() if self.student_combo.currentIndex() > 0 else None,
            'category_id': self.category_combo.currentData() if self.category_combo.currentIndex() > 0 else None,
            'course_id': self.course_combo.currentData() if self.course_combo.currentIndex() > 0 else None,
            'date_from': self.date_from.date().toString('yyyy-MM-dd') if self.date_from.date() else None,
            'date_to': self.date_to.date().toString('yyyy-MM-dd') if self.date_to.date() else None,
            'content': self.content_edit.text().strip() or None
        }
    
    def apply_filter(self):
        self.filter_changed.emit(self.get_filters())
    
    def clear_filter(self):
        self.student_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.date_from.setDate(QDate())
        self.date_to.setDate(QDate())
        self.content_edit.clear()
        self.filter_changed.emit({})
```

---

## Dependenies i Requisits

### Python Packages

```
PySide6>=6.4.0
pytest>=7.0.0
pytest-qt>=4.0.0
```

### Instal·lació

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## Testing

Tots els tests es basen en **pytest**.

### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py                 # Fixtures comunes
├── services/
│   ├── __init__.py
│   ├── test_directories.py     # Tests per directories.py
│   ├── test_student_service.py
│   ├── test_annotation_service.py
│   ├── test_category_service.py
│   ├── test_academic_course_service.py
│   └── ...
├── controllers/
│   └── ...
└── ui/
    └── ...
```

### Exemple de Test

```python
# tests/services/test_directories.py
import pytest
from pathlib import Path
import sys

# Mock sys.frozen per provar mode desenvolupament
def test_get_project_root_development():
    import tutopy.services.directories as dirs
    original_frozen = getattr(sys, 'frozen', False)
    try:
        sys.frozen = False
        result = dirs.get_project_root()
        assert isinstance(result, Path)
        # Ha de contenir un dels marcadors
        for marker in dirs.PROJECT_ROOT_MARKERS:
            if (result / marker).exists():
                break
        else:
            pytest.fail("Project root no conté cap marcador")
    finally:
        sys.frozen = original_frozen
```

---

## Executant l'Aplicació

```bash
# Desenvolupament
python tutopy/main.py

# Amb PyInstaller (futur)
pyinstaller --onefile --windowed --name "SeguimentAlumnes" tutopy/main.py
```

---

## Checklist d'Implementació

- [ ] main.py amb configuració Qt i HighDPI
- [ ] ui/styles.py amb colors i CSS global
- [ ] ui/main_window.py amb estructura base
- [ ] ui/widgets/sidebar.py
- [ ] ui/widgets/student_list.py
- [ ] ui/widgets/student_list_item.py
- [ ] ui/widgets/student_detail_panel.py
- [ ] ui/widgets/annotation_filter.py
- [ ] ui/tabs/annotations_tab.py
- [ ] ui/tabs/notes_tab.py
- [ ] ui/tabs/contacts_tab.py
- [ ] ui/tabs/documents_tab.py
- [ ] ui/dialogs/student_dialog.py
- [ ] ui/dialogs/annotation_dialog.py
- [ ] ui/dialogs/category_dialog.py
- [ ] ui/dialogs/academic_course_dialog.py
- [ ] controllers/student_controller.py
- [ ] controllers/annotation_controller.py
- [ ] controllers/main_controller.py
- [ ] Tests per diferents components
- [ ] Documentació actualitzada

---

## Notes Addicionals

1. **Seguretat**: No cal autenticació (execució local només)
2. **Backup**: No cal implementar còpies de seguretat automàtiques
3. **Exportació**: No cal exportar dades
4. **Idioma**: Exclusivament català
5. **Codificació**: UTF-8 en tots els texts
6. **Persistència**: SQLite local
7. **Concurrència**: No s'espera ús multi-usuari

---

*Document generat per Mistral Vibe*
