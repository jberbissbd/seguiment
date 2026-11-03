"""`QSplitter` amb un botó d'una icona al mànec per amagar/mostrar el primer panell.

Com un panell desplegable: en lloc d'un botó separat a la barra d'eines o
a sobre del panell, la icona viu al mateix mànec del separador, com als
IDE moderns.
"""

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF
from PySide6.QtWidgets import QSplitter, QSplitterHandle, QWidget

from tutopy.ui.styles import PRIMARY_COLOR, SURFACE_COLOR

TOGGLE_DIAMETER = 18
HANDLE_WIDTH = 20


class _CollapsibleSplitterHandle(QSplitterHandle):
    """Mànec de separador amb un botó circular al centre per plegar el primer panell."""

    def __init__(self, orientation: Qt.Orientation, parent: QSplitter):
        """Construeix el mànec, inicialment amb el primer panell desplegat."""
        super().__init__(orientation, parent)
        self._collapsed = False
        self._pressed_on_toggle = False

    def set_collapsed(self, collapsed: bool) -> None:
        """Actualitza quina fletxa es dibuixa, sense tocar la visibilitat del panell."""
        self._collapsed = collapsed
        self.update()

    def _toggle_rect(self) -> QRect:
        x = (self.width() - TOGGLE_DIAMETER) // 2
        y = (self.height() - TOGGLE_DIAMETER) // 2
        return QRect(x, y, TOGGLE_DIAMETER, TOGGLE_DIAMETER)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Dibuixa el mànec habitual i hi superposa el botó de plegar/desplegar."""
        super().paintEvent(event)
        rect = self._toggle_rect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(PRIMARY_COLOR), 1))
        painter.setBrush(QColor(SURFACE_COLOR))
        painter.drawEllipse(rect)
        self._draw_chevron(painter, rect)
        painter.end()

    def _draw_chevron(self, painter: QPainter, rect: QRect) -> None:
        center = rect.center()
        size = rect.width() * 0.22
        pointing_left = not self._collapsed
        dx = size if pointing_left else -size
        points = QPolygonF([
            QPointF(center.x() + dx, center.y() - size),
            QPointF(center.x() - dx, center.y()),
            QPointF(center.x() + dx, center.y() + size),
        ])
        pen = QPen(QColor(PRIMARY_COLOR), 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolyline(points)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Si el clic és sobre el botó, el reserva per plegar/desplegar en lloc d'arrossegar."""
        if self._toggle_rect().contains(event.position().toPoint()):
            self._pressed_on_toggle = True
            event.accept()
            return
        self._pressed_on_toggle = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Ignora l'arrossegament si el clic va començar sobre el botó."""
        if self._pressed_on_toggle:
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Commuta el primer panell si el clic i la deixada van ser sobre el botó."""
        if self._pressed_on_toggle:
            if self._toggle_rect().contains(event.position().toPoint()):
                splitter = self.splitter()
                if isinstance(splitter, CollapsibleSplitter):
                    splitter.toggle_first_panel()
            self._pressed_on_toggle = False
            event.accept()
            return
        super().mouseReleaseEvent(event)


class CollapsibleSplitter(QSplitter):
    """`QSplitter` de dos panells amb un botó al mànec per plegar el primer.

    El primer panell es redueix a mida zero amb `setSizes` en lloc
    d'amagar-se amb `setVisible(False)`: Qt amaga automàticament el mànec
    d'un panell ocult, cosa que faria desaparèixer també el botó per
    tornar-lo a mostrar. Reduir-lo a zero mantenint-lo visible evita
    aquest problema i el mànec (amb el seu botó) continua sempre
    disponible.
    """

    def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None):
        """Construeix el separador amb un mànec més ample per encabir el botó."""
        super().__init__(orientation, parent)
        self.setHandleWidth(HANDLE_WIDTH)
        self._collapsed = False
        self._expanded_width = 0
        self.splitterMoved.connect(self._sync_collapsed_from_drag)

    def createHandle(self) -> QSplitterHandle:
        """Retorna el mànec amb botó de plegar en lloc del mànec estàndard."""
        return _CollapsibleSplitterHandle(self.orientation(), self)

    def toggle_first_panel(self) -> None:
        """Redueix el primer panell a mida zero, o el torna a mostrar si ja ho estava."""
        panel = self.widget(0)
        if panel is None:
            return
        total = sum(self.sizes())
        if not self._collapsed:
            self._expanded_width = panel.minimumWidth() or self.sizes()[0] or 200
            panel.setMinimumWidth(0)
            self.setSizes([0, total])
        else:
            panel.setMinimumWidth(self._expanded_width)
            self.setSizes([self._expanded_width, max(0, total - self._expanded_width)])
        self._collapsed = not self._collapsed
        self._set_handle_collapsed(self._collapsed)

    def _sync_collapsed_from_drag(self, _pos: int, _index: int) -> None:
        """Manté la fletxa coherent si l'usuari arrossega el mànec en lloc de prémer el botó."""
        panel = self.widget(0)
        if panel is None:
            return
        collapsed = panel.width() == 0
        if collapsed != self._collapsed:
            self._collapsed = collapsed
            self._set_handle_collapsed(collapsed)

    def _set_handle_collapsed(self, collapsed: bool) -> None:
        handle = self.handle(1)
        if isinstance(handle, _CollapsibleSplitterHandle):
            handle.set_collapsed(collapsed)
