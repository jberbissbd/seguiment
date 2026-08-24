"""Execució de tasques sense bloquejar el fil principal de Qt."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Any

from PySide6.QtCore import QObject, Qt, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import QProgressDialog


class BackgroundTaskSignals(QObject):
    progress = Signal(int, int)
    succeeded = Signal(object)
    failed = Signal(object)


class BackgroundTask(QRunnable):
    """Executa una funció i permet cancel·lació cooperativa."""

    def __init__(self, operation: Callable[[Callable, Callable], Any]):
        super().__init__()
        self.operation = operation
        self.signals = BackgroundTaskSignals()
        self._cancelled = Event()

    def cancel(self) -> None:
        self._cancelled.set()

    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    @Slot()
    def run(self) -> None:
        try:
            result = self.operation(self.signals.progress.emit, self.is_cancelled)
        except Exception as error:
            self.signals.failed.emit(error)
            return
        self.signals.succeeded.emit(result)


class BackgroundTaskRunner:
    """Construeix i inicia tasques al conjunt global de fils de Qt."""

    def __init__(self, pool: QThreadPool | None = None):
        self.pool = pool or QThreadPool.globalInstance()

    def start(
        self,
        operation,
        *,
        on_progress=None,
        on_success=None,
        on_failure=None,
    ) -> BackgroundTask:
        task = BackgroundTask(operation)
        if on_progress is not None:
            task.signals.progress.connect(on_progress)
        if on_success is not None:
            task.signals.succeeded.connect(on_success)
        if on_failure is not None:
            task.signals.failed.connect(on_failure)
        self.pool.start(task)
        return task


class BackgroundOperationPresenter:
    """Coordina un `QProgressDialog` amb una `BackgroundTask`.

    Centralitza el patró, repetit a diversos controladors, de mostrar un
    diàleg de progrés modal mentre s'executa una operació en un fil
    secundari i tancar-lo automàticament en acabar (èxit, error o
    cancel·lació).
    """

    def __init__(
        self,
        window,
        task_runner: BackgroundTaskRunner | None = None,
        progress_dialog_factory=QProgressDialog,
    ):
        self.window = window
        self.task_runner = task_runner or BackgroundTaskRunner()
        self.progress_dialog_factory = progress_dialog_factory
        self.task: BackgroundTask | None = None
        self.progress: QProgressDialog | None = None

    def is_running(self) -> bool:
        return self.task is not None

    def start(
        self,
        operation: Callable[[Callable, Callable], Any],
        *,
        title: str,
        label: str,
        on_success: Callable[[Any], None],
        on_failure: Callable[[Exception], None],
        maximum: int = 0,
        cancellable: bool = True,
        progress_label: Callable[[int, int], str] | None = None,
    ) -> None:
        progress = self.progress_dialog_factory(
            label, "Cancel·lar" if cancellable else "", 0, maximum, self.window
        )
        progress.setWindowTitle(title)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        if cancellable:
            progress.setAutoClose(False)
            progress.setAutoReset(False)
        else:
            progress.setCancelButton(None)
        self.progress = progress

        def handle_progress(completed: int, total: int) -> None:
            progress = self.progress
            if progress is None:
                return
            progress.setMaximum(total)
            progress.setValue(completed)
            if progress_label is not None:
                progress.setLabelText(progress_label(completed, total))

        def handle_success(result: Any) -> None:
            self.close()
            on_success(result)

        def handle_failure(error: Exception) -> None:
            self.close()
            on_failure(error)

        self.task = self.task_runner.start(
            operation,
            on_progress=handle_progress,
            on_success=handle_success,
            on_failure=handle_failure,
        )
        if cancellable:
            progress.canceled.connect(self.task.cancel)
        progress.show()

    def close(self) -> None:
        progress = self.progress
        self.progress = None
        self.task = None
        if progress is not None:
            progress.close()
