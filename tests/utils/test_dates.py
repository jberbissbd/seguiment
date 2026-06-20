from tutopy.services.utils import DateConverter


class Test_conversio():

    def test_isotouser(self, iso_date_example):
        conversor = DateConverter()
        assert conversor.iso_to_display(iso_date_example) == "01/01/2026"

    def test_usertoiso(self, user_date_example):
        conversor = DateConverter()
        assert conversor.display_to_iso(user_date_example) == "2026-01-01"
