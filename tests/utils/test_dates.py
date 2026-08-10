import pytest
from tutopy.services.utils import DateConverter, AcademicCourseDeterminator


class TestConversio():
    """
    Tests per a comprovar la conversió de dates
    """

    def test_isotouser(self, iso_date_example):
        """Comprova que la conversió a format convencional es faci correctament"""
        conversor = DateConverter()
        assert conversor.iso_to_display(iso_date_example) == "01/01/2026"

    def test_usertoiso(self, user_date_example):
        """Comprova que la conversió a format ISO es faci correctament"""
        conversor = DateConverter()
        assert conversor.display_to_iso(user_date_example) == "2026-01-01"

    def test_error_isotouser(self):
        """Verifica que genera Value Error si al conversor no se li proporciona una cadena
            de text"""
        conversor_exemple_usuari = DateConverter()
        with pytest.raises(ValueError):
            a = conversor_exemple_usuari.display_to_iso(5)

    def test_error_user_to_iso(self):
        """Verifica que genera Value Error si al conversor no se li proporciona una cadena
            de text"""
        conversor_exemple_iso = DateConverter()
        with pytest.raises(ValueError):
            b = conversor_exemple_iso.iso_to_display(5)

class TestCursos():
    """Comprovació de la determinació dels cursos acadèmics"""

    def test_curs_singular(self):
        """Test amb els dos possibles casos de cursos"""
        data_prova_1 = "2026-01-01"
        data_prova_2 = "2026-09-01"
        converter = AcademicCourseDeterminator()
        assert converter.curs_academic_singular(data_prova_1) == "2025-2026"
        assert converter.curs_academic_singular(data_prova_2) == "2026-2027"
