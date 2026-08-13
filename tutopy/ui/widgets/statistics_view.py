from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from tutopy.ui.widgets.statistics_chart import BarChart


class StatisticsView(QWidget):
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        filters = QFrame()
        filters.setObjectName("panel")
        filter_layout = QGridLayout(filters)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.addWidget(QLabel("Curs acadèmic"), 0, 0)
        filter_layout.addWidget(QLabel("Grup"), 0, 1)
        filter_layout.addWidget(QLabel("Categoria"), 0, 2)
        self.course_input = QComboBox()
        self.group_input = QComboBox()
        self.category_input = QComboBox()
        filter_layout.addWidget(self.course_input, 1, 0)
        filter_layout.addWidget(self.group_input, 1, 1)
        filter_layout.addWidget(self.category_input, 1, 2)

        self.date_filter = QCheckBox("Limitar per dates")
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setDate(QDate.currentDate().addYears(-1))
        self.date_to.setDate(QDate.currentDate())
        self.date_from.setEnabled(False)
        self.date_to.setEnabled(False)
        self.refresh_button = QPushButton("Actualitzar")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.setDefault(True)
        self.refresh_button.setToolTip("Aplica els filtres seleccionats")
        dates = QHBoxLayout()
        dates.addWidget(self.date_filter)
        dates.addWidget(QLabel("Des de"))
        dates.addWidget(self.date_from)
        dates.addWidget(QLabel("fins a"))
        dates.addWidget(self.date_to)
        dates.addStretch()
        dates.addWidget(self.refresh_button)
        filter_layout.addLayout(dates, 2, 0, 1, 3)
        layout.addWidget(filters)

        summary = QHBoxLayout()
        self.summary_values = {}
        for key, title in (
            ("notes", "Notes"), ("covered", "Alumnes amb notes"),
            ("uncovered", "Sense notes"), ("average", "Mitjana per alumne"),
        ):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            label = QLabel("0")
            label.setObjectName("statValue")
            caption = QLabel(title)
            caption.setObjectName("mutedText")
            caption.setWordWrap(True)
            card_layout.addWidget(label)
            card_layout.addWidget(caption)
            self.summary_values[key] = label
            summary.addWidget(card, 1)
        layout.addLayout(summary)

        charts = QHBoxLayout()
        month_panel, self.month_chart = self._chart_panel(
            "Evolució mensual", show_latest=True
        )
        category_panel, self.category_chart = self._chart_panel("Notes per categoria")
        charts.addWidget(month_panel, 1)
        charts.addWidget(category_panel, 1)
        layout.addLayout(charts, 1)

        table_panel = QFrame()
        table_panel.setObjectName("panel")
        table_layout = QVBoxLayout(table_panel)
        table_title = QLabel("Cobertura per alumne")
        table_title.setObjectName("settingsTitle")
        self.context_label = QLabel("Tots els alumnes")
        self.context_label.setObjectName("mutedText")
        self.student_table = QTableWidget(0, 3)
        self.student_table.setHorizontalHeaderLabels(["Alumne", "Grup", "Notes"])
        self.student_table.setAlternatingRowColors(True)
        self.student_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.student_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.student_table.setSortingEnabled(True)
        self.student_table.verticalHeader().hide()
        header = self.student_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table_layout.addWidget(table_title)
        table_layout.addWidget(self.context_label)
        table_layout.addWidget(self.student_table)
        layout.addWidget(table_panel, 1)

        self.date_filter.toggled.connect(self.date_from.setEnabled)
        self.date_filter.toggled.connect(self.date_to.setEnabled)
        self.refresh_button.clicked.connect(self.refresh_requested)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(180)
        self._refresh_timer.timeout.connect(self.refresh_requested)
        self.course_input.currentIndexChanged.connect(self._schedule_refresh)
        self.group_input.currentIndexChanged.connect(self._schedule_refresh)
        self.category_input.currentIndexChanged.connect(self._schedule_refresh)
        self.date_filter.toggled.connect(self._schedule_refresh)
        self.date_from.dateChanged.connect(self._schedule_refresh)
        self.date_to.dateChanged.connect(self._schedule_refresh)

    @staticmethod
    def _chart_panel(title, show_latest=False):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        heading = QLabel(title)
        heading.setObjectName("settingsTitle")
        chart = BarChart(show_latest=show_latest)
        chart.setAccessibleName(title)
        layout.addWidget(heading)
        layout.addWidget(chart, 1)
        return panel, chart

    def set_filter_options(self, courses, groups, categories) -> None:
        selections = (
            (self.course_input, "Tots els cursos", [(item.course, item.id) for item in courses]),
            (self.group_input, "Tots els grups", [(item, item) for item in groups]),
            (self.category_input, "Totes les categories", [(item.name, item.id) for item in categories]),
        )
        for combo, all_label, values in selections:
            selected = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(all_label, None)
            for label, value in values:
                combo.addItem(label, value)
            index = combo.findData(selected)
            combo.setCurrentIndex(max(0, index))
            combo.blockSignals(False)

    def _schedule_refresh(self, _value=None) -> None:
        """Agrupa canvis consecutius per evitar consultes redundants."""
        self._refresh_timer.start()

    def filter_values(self) -> dict:
        dates_enabled = self.date_filter.isChecked()
        return {
            "course_id": self.course_input.currentData(),
            "group_name": self.group_input.currentData(),
            "category_id": self.category_input.currentData(),
            "date_from": self.date_from.date().toString(Qt.DateFormat.ISODate)
                         if dates_enabled else None,
            "date_to": self.date_to.date().toString(Qt.DateFormat.ISODate)
                       if dates_enabled else None,
        }

    def set_snapshot(self, snapshot, context: str) -> None:
        self.summary_values["notes"].setText(str(snapshot.note_count))
        self.summary_values["covered"].setText(str(snapshot.students_with_notes))
        self.summary_values["uncovered"].setText(str(snapshot.students_without_notes))
        self.summary_values["average"].setText(f"{snapshot.average_per_student:.1f}")
        self.month_chart.set_values(snapshot.by_month)
        self.category_chart.set_values(snapshot.by_category)
        self.context_label.setText(context)
        self.student_table.setSortingEnabled(False)
        self.student_table.setRowCount(len(snapshot.by_student))
        for row, item in enumerate(snapshot.by_student):
            self.student_table.setItem(row, 0, QTableWidgetItem(item.student_name))
            self.student_table.setItem(row, 1, QTableWidgetItem(item.group_name or "—"))
            count = QTableWidgetItem()
            count.setData(Qt.ItemDataRole.DisplayRole, item.note_count)
            count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row, 2, count)
        self.student_table.setSortingEnabled(True)
