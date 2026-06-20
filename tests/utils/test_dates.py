from tutopy.services.utils import DateConverter


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
