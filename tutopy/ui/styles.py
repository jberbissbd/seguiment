"""
Estils globals per a l'aplicació de Seguiment d'Alumnes.

Aquest mòdul conté el CSS de Qt (QSS) per garantir una aparença
consistent a totes les plataformes (Windows, Linux, macOS).

El disseny segueix un estil modern i usable, amb colors basats
en el disseny visual proporcionat.
"""

# Colors principals
PRIMARY_COLOR = "#4F8EF7"  # Blau principal
PRIMARY_HOVER = "#3A7BEF"
PRIMARY_PRESSED = "#2A6BD6"
BACKGROUND_COLOR = "#f5f7fa"
SIDEBAR_BACKGROUND = "#2c3e50"
SIDEBAR_TEXT = "#ecf0f1"
CARD_BACKGROUND = "#ffffff"
BORDER_COLOR = "#e0e0e0"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#666666"

# Colors per categories
CATEGORY_ACADEMIC_COLOR = "#d4edda"
CATEGORY_ACADEMIC_TEXT = "#155724"
CATEGORY_FAMILY_COLOR = "#d1ecf1"
CATEGORY_FAMILY_TEXT = "#0c5460"
CATEGORY_BEHAVIOR_COLOR = "#fff3cd"
CATEGORY_BEHAVIOR_TEXT = "#856404"


CENTRAL_STYLE = f"""/* =============================================================================
   FONTS - Consistent a totes les plataformes
   ============================================================================= */
QWidget {{
    font-family: "Segoe UI", "Ubuntu", "San Francisco", "Arial", sans-serif;
    font-size: 12px;
    color: {TEXT_PRIMARY};
}}

/* Font per a títols */
QLabel.title, QLabel.heading {{
    font-size: 16px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QLabel.subtitle {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}

QLabel.small {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
}}

/* =============================================================================
   FONS DE L'APLICACIÓ
   ============================================================================= */
QMainWindow {{
    background-color: {BACKGROUND_COLOR};
}}

/* =============================================================================
   BOTONS
   ============================================================================= */
QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 80px;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background-color: {PRIMARY_PRESSED};
}}

QPushButton:disabled {{
    background-color: #cccccc;
    color: #666666;
}}

/* Botons secundaris (ex: Editar, Eliminar) */
QPushButton.secondary {{
    background-color: #f8f9fa;
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
}}

QPushButton.secondary:hover {{
    background-color: #e9ecef;
}}

QPushButton.danger {{
    background-color: #dc3545;
    color: white;
}}

QPushButton.danger:hover {{
    background-color: #c82333;
}}

/* =============================================================================
   CAMPS DE TEXT
   ============================================================================= */
QLineEdit, QComboBox, QDateEdit, QPlainTextEdit, QTextEdit {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 6px 8px;
    background-color: white;
    font-size: 13px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, 
QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {PRIMARY_COLOR};
    outline: none;
}}

QLineEdit:disabled, QComboBox:disabled {{
    background-color: #f8f9fa;
    color: {TEXT_SECONDARY};
}}

/* =============================================================================
   LLISTES
   ============================================================================= */
QListWidget, QTableWidget {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: white;
    padding: 4px;
}}

QListWidget::item, QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {BORDER_COLOR};
}}

QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: #e8f0fe;
    color: {PRIMARY_COLOR};
}}

QListWidget::item:hover, QTableWidget::item:hover {{
    background-color: #f8f9fa;
}}

QHeaderView::section {{
    background-color: {BACKGROUND_COLOR};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
    font-weight: bold;
}}

/* =============================================================================
   SIDEBAR
   ============================================================================= */
QWidget#sidebar {{
    background-color: {SIDEBAR_BACKGROUND};
    color: {SIDEBAR_TEXT};
    border-right: 1px solid {BORDER_COLOR};
}}

QPushButton#sidebar_button {{
    background-color: transparent;
    color: {SIDEBAR_TEXT};
    text-align: left;
    padding: 12px 16px;
    border-radius: 0px;
    border: none;
    font-size: 13px;
}}

QPushButton#sidebar_button:hover {{
    background-color: #34495e;
}}

QPushButton#sidebar_button:checked {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}

QLabel#sidebar_title {{
    font-size: 18px;
    font-weight: bold;
    color: white;
    padding: 20px 16px;
    border-bottom: 1px solid #34495e;
}}

QLabel#sidebar_version {{
    font-size: 11px;
    color: #95a5a6;
    padding: 16px;
}}

/* =============================================================================
   CARDS
   ============================================================================= */
QWidget.card {{
    background-color: {CARD_BACKGROUND};
    border-radius: 8px;
    border: 1px solid {BORDER_COLOR};
    padding: 12px;
    margin: 4px;
}}

QWidget.card:hover {{
    border: 1px solid {PRIMARY_COLOR};
}}

/* =============================================================================
   TABS
   ============================================================================= */
QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: white;
}}

QTabBar::tab {{
    padding: 8px 16px;
    background-color: transparent;
    border: none;
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}

QTabBar::tab:selected {{
    color: {PRIMARY_COLOR};
    border-bottom: 2px solid {PRIMARY_COLOR};
}}

QTabBar::tab:hover {{
    background-color: #f8f9fa;
}}

/* =============================================================================
   TAGS DE CATEGORIA
   ============================================================================= */
QLabel.category-tag {{
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
    display: inline-block;
    margin: 2px;
}}

QLabel.category-tag.academic {{
    background-color: {CATEGORY_ACADEMIC_COLOR};
    color: {CATEGORY_ACADEMIC_TEXT};
}}

QLabel.category-tag.family {{
    background-color: {CATEGORY_FAMILY_COLOR};
    color: {CATEGORY_FAMILY_TEXT};
}}

QLabel.category-tag.behavior {{
    background-color: {CATEGORY_BEHAVIOR_COLOR};
    color: {CATEGORY_BEHAVIOR_TEXT};
}}

/* =============================================================================
   BARRES D'EINES
   ============================================================================= */
QToolBar {{
    background-color: white;
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 8px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 6px 12px;
}}

QToolButton:hover {{
    background-color: {BACKGROUND_COLOR};
}}

/* =============================================================================
   CAIXES DE DIÀLEG
   ============================================================================= */
QDialog {{
    background-color: white;
    border-radius: 8px;
    padding: 0px;
}}

QDialog QFormLayout {{
    margin: 16px;
}}

QDialogButtonBox {{
    margin-top: 16px;
}}

/* =============================================================================
   ESTIL PER A CERCA
   ============================================================================= */
QLineEdit#search_input {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 20px;
    padding: 8px 16px;
    background-color: white;
    font-size: 13px;
}}

QLineEdit#search_input:focus {{
    border: 1px solid {PRIMARY_COLOR};
    outline: none;
}}
"""


def get_central_style() -> str:
    """Retorna l'estil CSS central per a l'aplicació."""
    return CENTRAL_STYLE


def apply_global_style(app) -> None:
    """Aplica l'estil global a l'aplicació Qt.
    
    Args:
        app: L'aplicació QApplication o QGuiApplication
    """
    app.setStyleSheet(CENTRAL_STYLE)


def set_high_dpi(app) -> None:
    """Configura l'aplicació per suport HighDPI.
    
    Args:
        app: L'aplicació QApplication o QGuiApplication
    """
    from PySide6.QtCore import Qt
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
