"""Entrada de data combinant text lliure i selector visual."""

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QCalendarWidget, QHBoxLayout, QLineEdit, QMenu, QToolButton, QWidget,
    QWidgetAction,
)

from tutopy.ui.resources import set_button_icon


class DateInput(QWidget):
    """Entrada de data per teclat amb un calendari emergent alternatiu."""

    dateChanged = Signal(QDate)
    DATE_FORMAT = "dd/MM/yyyy"

    def __init__(self, date: QDate | None = None, parent: QWidget | None = None):
        """Inicialitza el camp amb `date` (o la data actual) i el calendari emergent.

        Args:
            date: Data inicial (`QDate`); si és `None` s'utilitza la data d'avui.
            parent: Widget pare de Qt.
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.editor = QLineEdit()
        self.editor.setPlaceholderText("DD/MM/AAAA")
        self.editor.setText((date or QDate.currentDate()).toString(self.DATE_FORMAT))
        self.calendar_button = QToolButton()
        set_button_icon(self.calendar_button, "calendar")
        self.calendar_button.setToolTip("Obrir el calendari")
        self.calendar_button.setObjectName("calendarButton")
        layout.addWidget(self.editor, 1)
        layout.addWidget(self.calendar_button)

        self.calendar = QCalendarWidget()
        self.menu = QMenu(self)
        action = QWidgetAction(self.menu)
        action.setDefaultWidget(self.calendar)
        self.menu.addAction(action)
        self.calendar_button.setMenu(self.menu)
        self.calendar_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.calendar.clicked.connect(self.setDate)
        self.editor.editingFinished.connect(self.interpretText)

    def lineEdit(self):
        """Retorna el `QLineEdit` intern per a integracions que el necessitin."""
        return self.editor

    def date(self) -> QDate:
        """Interpreta el text actual del camp com a `QDate` (invàlida si no ho és)."""
        return QDate.fromString(self.editor.text().strip(), self.DATE_FORMAT)

    def setDate(self, date: QDate) -> None:
        """Estableix `date` al camp de text i al calendari, i emet `dateChanged`.

        Args:
            date: Nova data; si és invàlida no fa res.
        """
        if not date.isValid():
            return
        self.editor.setText(date.toString(self.DATE_FORMAT))
        self.calendar.setSelectedDate(date)
        self.dateChanged.emit(date)
        self.menu.close()

    def interpretText(self) -> None:
        """Sincronitza el calendari amb el text escrit manualment, si és vàlid."""
        date = self.date()
        if date.isValid():
            self.calendar.setSelectedDate(date)
            self.dateChanged.emit(date)
