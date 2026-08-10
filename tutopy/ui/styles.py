PRIMARY_COLOR = "#2B73B7"
SECONDARY_COLOR = "#3D85C6"
ACCENT_COLOR = "#FF6B35"
BACKGROUND_COLOR = "#F5F7FA"
SURFACE_COLOR = "#FFFFFF"
TEXT_PRIMARY = "#2C3E50"
TEXT_SECONDARY = "#64748B"
SUCCESS_COLOR = "#27AE60"
WARNING_COLOR = "#F39C12"
ERROR_COLOR = "#E74C3C"
BORDER_COLOR = "#D8E0E8"


MAIN_STYLESHEET = f"""
QMainWindow, QDialog, QWidget#applicationRoot {{
    background-color: {BACKGROUND_COLOR};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
    font-size: 14px;
}}

QDialog {{
    background-color: {SURFACE_COLOR};
}}

QDialog QLabel {{
    color: {TEXT_PRIMARY};
}}

QFrame#sidebar {{
    background-color: #173A5E;
    border: none;
}}

QLabel#appTitle {{
    color: white;
    font-size: 22px;
    font-weight: 700;
    padding: 8px 4px 20px 4px;
}}

QPushButton[navButton="true"] {{
    background: transparent;
    color: #DCEAF7;
    border: none;
    border-radius: 6px;
    padding: 11px 12px;
    text-align: left;
    min-height: 24px;
}}

QPushButton[navButton="true"]:hover {{
    background-color: #234F7A;
}}

QPushButton[navButton="true"]:checked {{
    background-color: {PRIMARY_COLOR};
    color: white;
    font-weight: 600;
}}

QFrame#panel {{
    background-color: {SURFACE_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
}}

QFrame#studentSummary {{
    background-color: #F8FAFC;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
}}

QFrame#studentSummary QLabel {{
    background: transparent;
    border: none;
}}

QLabel#studentAvatar {{
    background-color: #E8EEFF;
    color: #405CF5;
    border: none;
    border-radius: 23px;
    font-size: 14px;
    font-weight: 700;
}}

QLabel#studentName {{
    color: {TEXT_PRIMARY};
    font-size: 16px;
    font-weight: 700;
}}

QLabel#studentMeta {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}

QLabel#sectionTitle {{
    color: {TEXT_PRIMARY};
    font-size: 20px;
    font-weight: 650;
}}

QLabel#mutedText {{
    color: {TEXT_SECONDARY};
}}

QLabel#errorText {{
    color: {ERROR_COLOR};
}}

QLineEdit, QComboBox, QDateEdit, QPlainTextEdit {{
    background-color: white;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 22px;
    selection-background-color: {PRIMARY_COLOR};
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QPlainTextEdit:focus {{
    border-color: {PRIMARY_COLOR};
}}

QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled,
QPlainTextEdit:disabled {{
    background-color: #EEF2F6;
    color: {TEXT_SECONDARY};
}}

QComboBox, QDateEdit {{
    padding-right: 28px;
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    border: none;
    width: 26px;
}}

QComboBox QAbstractItemView {{
    background-color: white;
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    selection-background-color: #E5F1FB;
    selection-color: {TEXT_PRIMARY};
    padding: 4px;
}}

QToolButton#calendarButton, QToolButton#selectorButton {{
    background-color: white;
    color: {PRIMARY_COLOR};
    border: 1px solid {PRIMARY_COLOR};
    border-radius: 6px;
    padding: 7px;
    min-width: 26px;
}}

QToolButton#calendarButton:hover, QToolButton#selectorButton:hover {{
    background-color: #EEF6FC;
}}

QPlainTextEdit {{
    min-height: 90px;
}}

QDialogButtonBox {{
    border-top: 1px solid #EDF1F5;
    padding-top: 12px;
}}

QDialogButtonBox QPushButton {{
    background-color: white;
    color: {PRIMARY_COLOR};
    border: 1px solid {PRIMARY_COLOR};
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 76px;
}}

QDialogButtonBox QPushButton:hover {{
    background-color: #EEF6FC;
}}

QDialogButtonBox QPushButton:default {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}

QDialogButtonBox QPushButton:default:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton#primaryButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton#secondaryButton {{
    background-color: white;
    color: {PRIMARY_COLOR};
    border: 1px solid {PRIMARY_COLOR};
    border-radius: 6px;
    padding: 8px 12px;
}}

QPushButton:disabled {{
    background-color: #EEF2F6;
    color: #94A3B8;
    border-color: #CBD5E1;
}}

QPushButton#dangerButton {{
    background-color: white;
    color: {ERROR_COLOR};
    border: 1px solid {ERROR_COLOR};
    border-radius: 6px;
    padding: 8px 12px;
}}

QListWidget {{
    background-color: white;
    border: none;
    outline: none;
}}

QListWidget::item {{
    border-bottom: 1px solid #EDF1F5;
    padding: 10px;
}}

QListWidget::item:selected {{
    background-color: #E5F1FB;
    color: {TEXT_PRIMARY};
}}

QListWidget#studentListWidget::item {{
    padding: 0;
    min-height: 52px;
}}

QLabel#studentListName {{
    color: {TEXT_PRIMARY};
    font-weight: 600;
}}

QLabel#studentListGroup {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}

QTableWidget {{
    background-color: white;
    alternate-background-color: #F8FAFC;
    border: 1px solid {BORDER_COLOR};
    gridline-color: #E8EDF2;
    selection-background-color: #DCECF9;
    selection-color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: #E9EFF5;
    color: {TEXT_PRIMARY};
    border: none;
    border-right: 1px solid {BORDER_COLOR};
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 8px;
    font-weight: 600;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    background-color: white;
    border-radius: 6px;
}}

QTabBar::tab {{
    background-color: #E9EFF5;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER_COLOR};
    border-bottom: none;
    padding: 9px 13px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: white;
    color: {PRIMARY_COLOR};
    font-weight: 600;
}}

QStatusBar {{
    background-color: #173A5E;
    color: white;
}}
"""
