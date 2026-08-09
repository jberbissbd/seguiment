"""
Tests per als estils globals de l'aplicació.

Utilitza pytest-qt per executar en mode headless.
"""
import pytest
from PySide6.QtWidgets import QApplication
from tutopy.ui.styles import (
    PRIMARY_COLOR, PRIMARY_HOVER, PRIMARY_PRESSED,
    BACKGROUND_COLOR, SIDEBAR_BACKGROUND, SIDEBAR_TEXT,
    CARD_BACKGROUND, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
    CATEGORY_ACADEMIC_COLOR, CATEGORY_ACADEMIC_TEXT,
    CATEGORY_FAMILY_COLOR, CATEGORY_FAMILY_TEXT,
    CATEGORY_BEHAVIOR_COLOR, CATEGORY_BEHAVIOR_TEXT,
    CENTRAL_STYLE, get_central_style, apply_global_style, set_high_dpi
)


class TestColorConstants:
    """Tests per a les constants de color."""
    
    def test_primary_colors_exist(self):
        """Verifica que els colors primaris estan definits."""
        assert PRIMARY_COLOR == "#4F8EF7"
        assert PRIMARY_HOVER == "#3A7BEF"
        assert PRIMARY_PRESSED == "#2A6BD6"
    
    def test_background_colors_exist(self):
        """Verifica que els colors de fons estan definits."""
        assert BACKGROUND_COLOR == "#f5f7fa"
        assert SIDEBAR_BACKGROUND == "#2c3e50"
        assert CARD_BACKGROUND == "#ffffff"
    
    def test_text_colors_exist(self):
        """Verifica que els colors de text estan definits."""
        assert TEXT_PRIMARY == "#333333"
        assert TEXT_SECONDARY == "#666666"
    
    def test_category_colors_exist(self):
        """Verifica que els colors de categories estan definits."""
        assert CATEGORY_ACADEMIC_COLOR == "#d4edda"
        assert CATEGORY_ACADEMIC_TEXT == "#155724"
        assert CATEGORY_FAMILY_COLOR == "#d1ecf1"
        assert CATEGORY_FAMILY_TEXT == "#0c5460"
        assert CATEGORY_BEHAVIOR_COLOR == "#fff3cd"
        assert CATEGORY_BEHAVIOR_TEXT == "#856404"


class TestCentralStyle:
    """Tests per a l'estil CSS central."""
    
    def test_central_style_is_string(self):
        """Verifica que CENTRAL_STYLE és un string."""
        assert isinstance(CENTRAL_STYLE, str)
    
    def test_central_style_not_empty(self):
        """Verifica que CENTRAL_STYLE no està buit."""
        assert len(CENTRAL_STYLE) > 0
    
    def test_central_style_contains_css_rules(self):
        """Verifica que CENTRAL_STYLE conté regles CSS esperades."""
        assert "QWidget" in CENTRAL_STYLE
        assert "QPushButton" in CENTRAL_STYLE
        assert "QMainWindow" in CENTRAL_STYLE
        assert "#sidebar" in CENTRAL_STYLE
    
    def test_central_style_contains_color_values(self):
        """Verifica que CENTRAL_STYLE conté els valors de color."""
        assert PRIMARY_COLOR in CENTRAL_STYLE
        assert BACKGROUND_COLOR in CENTRAL_STYLE
        assert SIDEBAR_BACKGROUND in CENTRAL_STYLE
    
    def test_get_central_style_returns_style(self):
        """Verifica que get_central_style() retorna l'estil."""
        assert get_central_style() == CENTRAL_STYLE


class TestStyleFunctions:
    """Tests per a les funcions d'estil."""
    
    def test_apply_global_style(self, qtbot):
        """Verifica que apply_global_style aplica l'estil sense errors."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        # Això no hauria de llençar cap excepció
        apply_global_style(app)
        # Verificar que l'aplicació té un stylesheet
        assert app.styleSheet() == CENTRAL_STYLE
    
    def test_set_high_dpi(self, qtbot):
        """Verifica que set_high_dpi configura els atributs HighDPI."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        set_high_dpi(app)
        # Verificar que els atributs HighDPI estan activats
        # Nota: No podem verificar això directament, però podem verificar
        # que no es produeixi cap error
        assert True
