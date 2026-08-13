from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget


class BarChart(QWidget):
    """Gràfic lleuger amb alternativa textual per accessibilitat."""

    def __init__(self, parent=None, show_latest=False, max_items=12):
        super().__init__(parent)
        self._values = ()
        self._show_latest = show_latest
        self._max_items = max_items
        self.setMinimumHeight(210)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Gràfic de barres")

    def set_values(self, values) -> None:
        self._values = tuple(values)
        visible_count = (
            len(self._values) if self._max_items is None
            else min(len(self._values), self._max_items)
        )
        self.setMinimumWidth(max(320, visible_count * 105))
        description = "; ".join(
            f"{item.label}: {item.value}" for item in self._values
        ) or "No hi ha dades per mostrar"
        self.setAccessibleDescription(description)
        self.setToolTip(description)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        if not self._values:
            painter.setPen(QColor("#64748B"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No hi ha dades per als filtres seleccionats")
            return
        if self._max_items is None:
            visible = self._values
        elif self._show_latest:
            visible = self._values[-self._max_items:]
        else:
            visible = self._values[:self._max_items]
        bounds = self.rect().adjusted(42, 18, -16, -42)
        maximum = max(item.value for item in visible) or 1
        gap = 8
        bar_width = max(8.0, (bounds.width() - gap * (len(visible) - 1)) / len(visible))
        metrics = QFontMetrics(painter.font())
        painter.setPen(QPen(QColor("#D8E0E8"), 1))
        painter.drawLine(bounds.bottomLeft(), bounds.bottomRight())
        for index, item in enumerate(visible):
            height = bounds.height() * item.value / maximum
            x = bounds.left() + index * (bar_width + gap)
            bar = QRectF(x, bounds.bottom() - height, bar_width, height)
            painter.fillRect(bar, QColor("#2B73B7"))
            painter.setPen(QColor("#2C3E50"))
            painter.drawText(
                QRectF(x, bar.top() - 22, bar_width, 20),
                Qt.AlignmentFlag.AlignCenter, str(item.value),
            )
            label = metrics.elidedText(item.label, Qt.TextElideMode.ElideRight,
                                       max(8, int(bar_width + gap)))
            painter.drawText(
                QRectF(x - gap / 2, bounds.bottom() + 8, bar_width + gap, 24),
                Qt.AlignmentFlag.AlignCenter, label,
            )
