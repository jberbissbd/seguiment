from threading import get_ident

from PySide6.QtCore import QThreadPool

from tutopy.ui.background_task import BackgroundTask


def test_tasca_s_executa_fora_del_fil_principal(qtbot):
    main_thread = get_ident()
    task = BackgroundTask(lambda _progress, _cancelled: get_ident())

    with qtbot.waitSignal(task.signals.succeeded, timeout=2000) as signal:
        QThreadPool.globalInstance().start(task)

    assert signal.args[0] != main_thread


def test_tasca_propaga_errors_al_fil_principal(qtbot):
    def fail(_progress, _cancelled):
        raise RuntimeError("error simulat")

    task = BackgroundTask(fail)
    with qtbot.waitSignal(task.signals.failed, timeout=2000) as signal:
        QThreadPool.globalInstance().start(task)

    assert isinstance(signal.args[0], RuntimeError)
    assert str(signal.args[0]) == "error simulat"
