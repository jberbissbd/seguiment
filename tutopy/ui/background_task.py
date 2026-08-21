"""Execució de tasques sense bloquejar el fil principal de Qt."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


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
