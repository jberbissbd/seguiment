import pytest
from tutopy.services.utils import get_app_dir, DateConverter, AcademicCourseDeterminator


class TestGetAppDir:
    """Tests per a la funció get_app_dir."""

    def test_returns_directory_path(self):
        """Testa que get_app_dir retorna un path vàlid."""
        app_dir = get_app_dir()
        assert isinstance(app_dir, str)
        assert len(app_dir) > 0


class TestDateConverter:
    """Tests per a la classe DateConverter."""

    def test_iso_to_display_valid_date(self):
        """Testa la conversió d'ISO a format de visualització."""
        converter = DateConverter()
        
        # Cas normal
        assert converter.iso_to_display("2026-01-15") == "15/01/2026"
        assert converter.iso_to_display("2025-12-31") == "31/12/2025"
        assert converter.iso_to_display("2000-02-29") == "29/02/2000"  # Any de traspàs

    def test_iso_to_display_invalid_input_type(self):
        """Testa que iso_to_display llança ValueError per tipus no string."""
        converter = DateConverter()
        
        with pytest.raises(ValueError, match="L'input de la funció ha de ser una cadena de"):
            converter.iso_to_display(123)
        
        with pytest.raises(ValueError, match="L'input de la funció ha de ser una cadena de"):
            converter.iso_to_display(None)
        
        with pytest.raises(ValueError, match="L'input de la funció ha de ser una cadena de"):
            converter.iso_to_display([2026, 1, 15])

    def test_display_to_iso_valid_date(self):
        """Testa la conversió de format de visualització a ISO."""
        converter = DateConverter()
        
        # Cas normal
        assert converter.display_to_iso("15/01/2026") == "2026-01-15"
        assert converter.display_to_iso("31/12/2025") == "2025-12-31"
        assert converter.display_to_iso("01/01/2000") == "2000-01-01"

    def test_display_to_iso_invalid_input_type(self):
        """Testa que display_to_iso llança ValueError per tipus no string."""
        converter = DateConverter()
        
        with pytest.raises(ValueError, match="L'input de la funció ha de ser una cadena de"):
            converter.display_to_iso(123)
        
        with pytest.raises(ValueError, match="L'input de la funció ha de ser una cadena de"):
            converter.display_to_iso(None)


class TestAcademicCourseDeterminator:
    """Tests per a la classe AcademicCourseDeterminator."""

    def test_september_to_june_returns_previous_year(self):
        """Testa que dates de gener a agost retornen el curs anterior."""
        determinator = AcademicCourseDeterminator()
        
        # Gener a Agost (mes 1-8) -> curs anterior
        assert determinator.curs_academic_singular("2026-01-15") == "2025-2026"
        assert determinator.curs_academic_singular("2026-02-28") == "2025-2026"
        assert determinator.curs_academic_singular("2026-03-15") == "2025-2026"
        assert determinator.curs_academic_singular("2026-04-01") == "2025-2026"
        assert determinator.curs_academic_singular("2026-05-30") == "2025-2026"
        assert determinator.curs_academic_singular("2026-06-15") == "2025-2026"
        assert determinator.curs_academic_singular("2026-07-31") == "2025-2026"
        assert determinator.curs_academic_singular("2026-08-31") == "2025-2026"

    def test_september_to_december_returns_current_year(self):
        """Testa que dates de setembre a desembre retornen el curs actual."""
        determinator = AcademicCourseDeterminator()
        
        # Setembre a Desembre (mes 9-12) -> curs actual
        assert determinator.curs_academic_singular("2026-09-01") == "2026-2027"
        assert determinator.curs_academic_singular("2026-10-15") == "2026-2027"
        assert determinator.curs_academic_singular("2026-11-30") == "2026-2027"
        assert determinator.curs_academic_singular("2026-12-25") == "2026-2027"

    def test_edge_cases(self):
        """Testa casos límit."""
        determinator = AcademicCourseDeterminator()
        
        # 1 de setembre (inici del curs nou)
        assert determinator.curs_academic_singular("2026-09-01") == "2026-2027"
        
        # 31 d'agost (final del curs anterior)
        assert determinator.curs_academic_singular("2026-08-31") == "2025-2026"
        
        # Anys de traspàs
        assert determinator.curs_academic_singular("2024-02-29") == "2023-2024"

    def test_invalid_date_format(self):
        """Testa que dates amb format invàlid generen errors."""
        determinator = AcademicCourseDeterminator()
        
        # Format amb només 1 part: llança IndexError per accés a parts_curs[1]
        with pytest.raises(IndexError):
            determinator.curs_academic_singular("2026")
        
        # Format amb text no numèric: llança ValueError
        with pytest.raises(ValueError):
            determinator.curs_academic_singular("invalid")
        
        # Format amb 2 parts: "2026-01" -> parts_curs = ["2026", "01"]
        # El mètode només usa [0] i [1], així que funcione correctament
        assert determinator.curs_academic_singular("2026-01") == "2025-2026"
        
        # Mes no numèric: llança ValueError
        with pytest.raises(ValueError):
            determinator.curs_academic_singular("2026-abc-01")
