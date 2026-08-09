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
QMainWindow, QWidget#applicationRoot {{
    background-color: {BACKGROUND_COLOR};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
    font-size: 14px;
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
    padding: 11px 14px;
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

QLineEdit {{
    background-color: white;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 22px;
}}

QLineEdit:focus {{
    border-color: {PRIMARY_COLOR};
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
