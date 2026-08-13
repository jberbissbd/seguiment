from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy

from tutopy.models.statistics import (
    StatisticValue, StatisticsSnapshot, StudentStatistic,
)
from tutopy.ui.main_window import MainWindow
from tutopy.ui.widgets.statistics_view import StatisticsView


def test_vista_exposa_filtres_i_actualitzacio_explicita(qtbot):
    view = StatisticsView()
    qtbot.addWidget(view)
    view.set_filter_options([], ["4t A"], [])
    view.group_input.setCurrentIndex(1)
    view.date_filter.setChecked(True)

    with qtbot.waitSignal(view.refresh_requested):
        qtbot.mouseClick(view.refresh_button, Qt.MouseButton.LeftButton)

    assert view.filter_values()["group_name"] == "4t A"
    assert view.filter_values()["date_from"] is not None
    assert view.date_from.isEnabled()


def test_canviar_un_filtre_actualitza_automaticament_una_sola_vegada(qtbot):
    view = StatisticsView()
    qtbot.addWidget(view)
    view.set_filter_options([], ["4t A", "4t B"], [])

    signal = QSignalSpy(view.refresh_requested)
    view.group_input.setCurrentIndex(1)
    view.group_input.setCurrentIndex(2)
    qtbot.waitUntil(lambda: signal.count() == 1, timeout=1_000)
    qtbot.wait(220)

    assert signal.count() == 1
    assert view.filter_values()["group_name"] == "4t B"


def test_vista_mostra_resum_grafics_i_alumnes_amb_zero(qtbot):
    view = StatisticsView()
    qtbot.addWidget(view)
    snapshot = StatisticsSnapshot(
        note_count=2, student_count=2, students_with_notes=1,
        students_without_notes=1, average_per_student=1.0,
        by_month=(StatisticValue("2026-02", 2),),
        by_category=(StatisticValue("Acadèmic", 2),),
        by_student=(
            StudentStatistic(1, "Martí, Laia", "4t A", 2),
            StudentStatistic(2, "Puig, Pau", "4t A", 0),
        ),
    )
    view.set_snapshot(snapshot, "2 alumnes inclosos")

    assert view.summary_values["notes"].text() == "2"
    assert view.summary_values["uncovered"].text() == "1"
    assert view.student_table.rowCount() == 2
    assert "2026-02: 2" in view.month_chart.accessibleDescription()
    assert view.context_label.text() == "2 alumnes inclosos"


def test_nova_seccio_es_navegable_i_te_desplacament_vertical(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_section("statistics")
    assert window.content_stack.currentWidget() is window._pages["statistics"]
    assert window.sidebar.buttons["statistics"].isChecked()
    assert window.statistics_scroll.widget() is window.statistics_view
