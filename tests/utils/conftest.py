import pytest

@pytest.fixture(scope='module')
def iso_date_example():
    """Proporciona una data en el format ISO"""
    return "2026-01-01"

@pytest.fixture(scope='module')
def user_date_example():
    """Proporciona una data en el format en el que el veurà l'usuari"""
    return "01/01/2026"
