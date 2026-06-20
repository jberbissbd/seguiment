import pytest

@pytest.fixture(scope='module')
def iso_date_example():
    return "2026-01-01"

@pytest.fixture(scope='module')
def user_date_example():
    return "01/01/2026"