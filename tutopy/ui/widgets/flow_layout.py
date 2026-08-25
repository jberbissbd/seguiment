"""Layout Qt personalitzat que distribueix widgets en diverses línies.

Útil per a col·leccions de mida variable (com les etiquetes de descriptors
d'un alumne) que s'han d'ajustar a l'amplada disponible sense wrapping
manual.
"""

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout


class FlowLayout(QLayout):
    """Layout compacte que distribueix widgets en diverses línies."""

    def __init__(self, parent=None, margin=0, spacing=6):
        """Inicialitza el layout amb els marges i l'espaiat indicats."""
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        """Afegeix un `QLayoutItem` al final del flux (protocol `QLayout`)."""
        self._items.append(item)

    def count(self):
        """Retorna el nombre d'elements gestionats pel layout."""
        return len(self._items)

    def itemAt(self, index):
        """Retorna l'element a `index`, o `None` si és fora de rang."""
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        """Treu i retorna l'element a `index`, o `None` si és fora de rang."""
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        """Indica que el layout no s'expandeix en cap direcció fixa."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        """Indica que l'alçada depèn de l'amplada disponible."""
        return True

    def heightForWidth(self, width):
        """Calcula l'alçada necessària per encabir els elements a `width`."""
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        """Recol·loca els elements dins `rect` seguint el flux de línies."""
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        """Retorna la mida mínima com a suggeriment de mida."""
        return self.minimumSize()

    def minimumSize(self):
        """Calcula la mida mínima que engloba tots els elements i els marges."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

    def clear(self):
        """Elimina tots els widgets del layout i els allibera."""
        while self.count():
            item = self.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _do_layout(self, rect, test_only):
        x, y, line_height = rect.x(), rect.y(), 0
        for item in self._items:
            size = item.sizeHint()
            next_x = x + size.width() + self.spacing()
            if next_x - self.spacing() > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + self.spacing()
                next_x = x + size.width() + self.spacing()
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), size))
            x = next_x
            line_height = max(line_height, size.height())
        return y + line_height - rect.y()
