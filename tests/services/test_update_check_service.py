import json
import urllib.error
from contextlib import contextmanager

import pytest

from tutopy.services.update_check_service import UpdateCheckService, _is_newer


def _fake_response(payload: dict):
    @contextmanager
    def urlopen(_request, timeout=None):
        class Response:
            def read(self):
                return json.dumps(payload).encode("utf-8")

        yield Response()

    return urlopen


def _service(monkeypatch, current_version="1.3.2", payload=None, raises=None):
    service = UpdateCheckService(current_version=current_version)
    if raises is not None:
        def urlopen(_request, timeout=None):
            raise raises

        monkeypatch.setattr(
            "tutopy.services.update_check_service.urllib.request.urlopen", urlopen
        )
    else:
        monkeypatch.setattr(
            "tutopy.services.update_check_service.urllib.request.urlopen",
            _fake_response(payload),
        )
    return service


def test_detecta_una_versio_mes_recent(monkeypatch):
    service = _service(monkeypatch, current_version="1.3.2", payload={
        "tag_name": "v1.4.0", "html_url": "https://example.test/releases/v1.4.0",
    })

    result = service.check_for_update()

    assert result.update_available is True
    assert result.latest_version == "1.4.0"
    assert result.release_url == "https://example.test/releases/v1.4.0"


def test_no_avisa_si_la_versio_es_igual_o_anterior(monkeypatch):
    service = _service(monkeypatch, current_version="1.4.0", payload={
        "tag_name": "v1.4.0", "html_url": "https://example.test/releases/v1.4.0",
    })

    result = service.check_for_update()

    assert result.update_available is False
    assert result.latest_version == "1.4.0"


def test_resposta_sense_tag_name_no_avisa_ni_falla(monkeypatch):
    service = _service(monkeypatch, current_version="1.3.2", payload={
        "html_url": "https://example.test/releases/latest",
    })

    result = service.check_for_update()

    assert result == service.check_for_update()
    assert result.update_available is False
    assert result.latest_version is None


def test_error_de_xarxa_no_llenca_i_no_avisa(monkeypatch):
    service = _service(
        monkeypatch, raises=urllib.error.URLError("sense connexió")
    )

    result = service.check_for_update()

    assert result.update_available is False
    assert result.latest_version is None
    assert result.release_url is None


def test_timeout_no_llenca_i_no_avisa(monkeypatch):
    service = _service(monkeypatch, raises=TimeoutError("massa lent"))

    result = service.check_for_update()

    assert result.update_available is False


def test_resposta_amb_json_invalid_no_llenca(monkeypatch):
    def urlopen(_request, timeout=None):
        class Response:
            def read(self):
                return b"no es json"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return Response()

    monkeypatch.setattr(
        "tutopy.services.update_check_service.urllib.request.urlopen", urlopen
    )
    service = UpdateCheckService(current_version="1.3.2")

    result = service.check_for_update()

    assert result.update_available is False


@pytest.mark.parametrize(("remote", "local", "expected"), [
    ("1.3.10", "1.3.2", True),
    ("1.3.2", "1.3.10", False),
    ("1.4.0", "1.3.9", True),
    ("1.3.2", "1.3.2", False),
    ("1.3.2", "1.4.0", False),
    ("1.3.beta", "1.3.2", False),
])
def test_is_newer_compara_versions_per_components_numerics(remote, local, expected):
    assert _is_newer(remote, local) is expected
