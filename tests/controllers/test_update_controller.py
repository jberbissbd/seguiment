import json
from contextlib import contextmanager

import pytest

from tutopy.application import create_services
from tutopy.controllers.update_controller import UpdateController
from tutopy.database.database import Database
from tutopy.ui.main_window import MainWindow


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "update-controller.db")).connect()
    yield database
    database.close()


class SynchronousTaskRunner:
    """Executa l'operació immediatament, sense `QThreadPool`.

    Evita dependre del planificador de fils de Qt (font de parpelleig en
    entorns de proves sandboxed): aquí es verifica el cablejat del
    controlador, no el funcionament de `BackgroundTaskRunner`, que ja es fa
    servir amb fils reals en altres controladors.
    """

    def start(self, operation, *, on_progress=None, on_success=None, on_failure=None):
        try:
            result = operation(lambda *_args: None, lambda: False)
        except Exception as error:  # noqa: BLE001 - replica el comportament real
            if on_failure is not None:
                on_failure(error)
            return None
        if on_success is not None:
            on_success(result)
        return None


class FakeDialog:
    created = []

    def __init__(self, latest_version, release_url, parent=None):
        self.latest_version = latest_version
        self.release_url = release_url
        self.parent = parent
        self.executed = False
        FakeDialog.created.append(self)

    def exec(self):
        self.executed = True


def _respond_with(payload: dict):
    @contextmanager
    def urlopen(_request, timeout=None):
        class Response:
            def read(self):
                return json.dumps(payload).encode("utf-8")

        yield Response()

    return urlopen


def _controller(db, qtbot, monkeypatch, payload):
    FakeDialog.created = []
    monkeypatch.setattr(
        "tutopy.services.update_check_service.urllib.request.urlopen",
        _respond_with(payload),
    )
    services = create_services(db)
    window = MainWindow()
    qtbot.addWidget(window)
    controller = UpdateController(
        window, services.update_check, services.preferences,
        task_runner=SynchronousTaskRunner(), dialog_factory=FakeDialog,
    )
    return services, window, controller


def test_mostra_un_avis_quan_hi_ha_una_versio_mes_recent(db, qtbot, monkeypatch):
    _services, _window, controller = _controller(db, qtbot, monkeypatch, {
        "tag_name": "v99.0.0", "html_url": "https://example.test/releases/v99.0.0",
    })

    controller.start()

    assert len(FakeDialog.created) == 1
    dialog = FakeDialog.created[0]
    assert dialog.latest_version == "99.0.0"
    assert dialog.release_url == "https://example.test/releases/v99.0.0"
    assert dialog.executed is True


def test_no_mostra_res_quan_no_hi_ha_versio_nova(db, qtbot, monkeypatch):
    _services, _window, controller = _controller(db, qtbot, monkeypatch, {
        "tag_name": "v0.0.1", "html_url": "https://example.test/releases/v0.0.1",
    })

    controller.start()

    assert FakeDialog.created == []


def test_no_fa_cap_comprovacio_si_la_preferencia_esta_desactivada(db, qtbot, monkeypatch):
    calls = []

    def urlopen(_request, timeout=None):
        calls.append(True)
        raise AssertionError("no s'hauria de consultar la xarxa")

    monkeypatch.setattr(
        "tutopy.services.update_check_service.urllib.request.urlopen", urlopen
    )
    services = create_services(db)
    services.preferences.set_update_check_enabled(False)
    window = MainWindow()
    qtbot.addWidget(window)
    FakeDialog.created = []
    controller = UpdateController(
        window, services.update_check, services.preferences,
        task_runner=SynchronousTaskRunner(), dialog_factory=FakeDialog,
    )

    controller.start()

    assert calls == []
    assert FakeDialog.created == []


def test_un_error_de_xarxa_no_mostra_cap_dialeg(db, qtbot, monkeypatch):
    def urlopen(_request, timeout=None):
        raise OSError("sense connexió")

    monkeypatch.setattr(
        "tutopy.services.update_check_service.urllib.request.urlopen", urlopen
    )
    services = create_services(db)
    window = MainWindow()
    qtbot.addWidget(window)
    FakeDialog.created = []
    controller = UpdateController(
        window, services.update_check, services.preferences,
        task_runner=SynchronousTaskRunner(), dialog_factory=FakeDialog,
    )

    controller.start()

    assert FakeDialog.created == []


def test_excepcio_inesperada_no_mostra_cap_dialeg_ni_es_propaga(db, qtbot):
    class FailingUpdateCheck:
        def check_for_update(self):
            raise RuntimeError("error inesperat")

    services = create_services(db)
    window = MainWindow()
    qtbot.addWidget(window)
    FakeDialog.created = []
    controller = UpdateController(
        window, FailingUpdateCheck(), services.preferences,
        task_runner=SynchronousTaskRunner(), dialog_factory=FakeDialog,
    )

    controller.start()  # no ha de llençar cap excepció

    assert FakeDialog.created == []


def test_marcar_la_casella_desa_la_preferencia(db, qtbot, monkeypatch):
    services, window, _controller_instance = _controller(db, qtbot, monkeypatch, {
        "tag_name": "v0.0.1", "html_url": "https://example.test/releases/v0.0.1",
    })

    window.data_tools.update_check_checkbox.setChecked(False)

    assert services.preferences.is_update_check_enabled() is False
