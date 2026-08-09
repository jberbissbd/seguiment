"""
Tests per al Sidebar de l'aplicació.

Utilitza pytest-qt per executar en mode headless.
"""
import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from tutopy.ui.widgets.sidebar import Sidebar


@pytest.fixture
def sidebar(qtbot):
    """Fixture que crea un Sidebar amb pytest-qt."""
    sidebar = Sidebar()
    qtbot.addWidget(sidebar)
    return sidebar


class TestSidebarInitialization:
    """Tests per a la inicialització del Sidebar."""
    
    def test_sidebar_creation(self, sidebar):
        """Verifica que el Sidebar es crea correctament."""
        assert sidebar is not None
        assert isinstance(sidebar, Sidebar)
    
    def test_sidebar_has_title(self, sidebar):
        """Verifica que el Sidebar té un títol."""
        assert sidebar.title_label is not None
        assert "Seguiment" in sidebar.title_label.text()
    
    def test_sidebar_has_version(self, sidebar):
        """Verifica que el Sidebar té una versió."""
        assert sidebar.version_label is not None
        assert sidebar.version_label.text() == "v0.0.1"


class TestSidebarNavigationButtons:
    """Tests per als botons de navegació del Sidebar."""
    
    def test_sidebar_has_nav_buttons(self, sidebar):
        """Verifica que el Sidebar té botons de navegació."""
        assert len(sidebar.nav_buttons) > 0
        assert "alumnes" in sidebar.nav_buttons
        assert "descriptors" in sidebar.nav_buttons
        assert "documents" in sidebar.nav_buttons
        assert "informes" in sidebar.nav_buttons
        assert "copia" in sidebar.nav_buttons
    
    def test_alumnes_button_checked_by_default(self, sidebar):
        """Verifica que el botó Alumnes està seleccionat per defecte."""
        assert sidebar.btn_alumnes.isChecked()
    
    def test_other_buttons_not_checked_by_default(self, sidebar):
        """Verifica que els altres botons no estan seleccionats per defecte."""
        assert not sidebar.btn_descriptors.isChecked()
        assert not sidebar.btn_documents.isChecked()
        assert not sidebar.btn_informes.isChecked()
        assert not sidebar.btn_copia.isChecked()


class TestSidebarNewStudentButton:
    """Tests per al botó Nou alumne del Sidebar."""
    
    def test_sidebar_has_new_student_button(self, sidebar):
        """Verifica que el Sidebar té el botó Nou alumne."""
        assert sidebar.btn_new_student is not None
        assert "Nou alumne" in sidebar.btn_new_student.text()


class TestSidebarSignals:
    """Tests per als senyals del Sidebar."""
    
    def test_new_student_signal_emitted(self, sidebar, qtbot):
        """Verifica que el senyal new_student_requested s'emet quan es clica."""
        mock_slot = MagicMock()
        sidebar.new_student_requested.connect(mock_slot)
        
        # Simular clic
        with qtbot.capture_exceptions():
            qtbot.mouseClick(sidebar.btn_new_student, Qt.MouseButton.LeftButton)
        
        # Verificar que el senyal s'ha emès
        mock_slot.assert_called_once()


class TestSidebarNavigation:
    """Tests per a la navegació del Sidebar."""
    
    def test_nav_button_click_selects_button(self, sidebar, qtbot):
        """Verifica que clicar un botó de navegació el selecciona."""
        # Clicar el botó Descriptors
        with qtbot.capture_exceptions():
            qtbot.mouseClick(sidebar.btn_descriptors, Qt.MouseButton.LeftButton)
        
        # Verificar que només el botó Descriptors està seleccionat
        assert not sidebar.btn_alumnes.isChecked()
        assert sidebar.btn_descriptors.isChecked()
        assert not sidebar.btn_documents.isChecked()
        assert not sidebar.btn_informes.isChecked()
        assert not sidebar.btn_copia.isChecked()
    
    def test_nav_button_click_deselects_others(self, sidebar, qtbot):
        """Verifica que clicar un botó desselecciona els altres."""
        # Seleccionar Documents
        with qtbot.capture_exceptions():
            qtbot.mouseClick(sidebar.btn_documents, Qt.MouseButton.LeftButton)
        assert sidebar.btn_documents.isChecked()
        
        # Seleccionar Informes
        with qtbot.capture_exceptions():
            qtbot.mouseClick(sidebar.btn_informes, Qt.MouseButton.LeftButton)
        assert sidebar.btn_informes.isChecked()
        assert not sidebar.btn_documents.isChecked()
