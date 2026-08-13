from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDialog, QFrame, QHeaderView, QLabel

from tutopy.models.messaging import AcademicCourse, Category
from tutopy.models.reporting import TermConfiguration
from tutopy.ui.dialogs.report_export_dialog import ReportExportDialog
from tutopy.ui.dialogs.term_configuration_dialog import TermConfigurationDialog
from tutopy.ui.widgets.data_tools import DataToolsView
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel


def test_dialog_configuracio_retorna_nomes_curs_grup_i_inicis(qtbot):
    course = AcademicCourse(3, "2025-2026")
    dialog = TermConfigurationDialog([course], ["4t A"])
    qtbot.addWidget(dialog)
    dialog.group_input.setCurrentText("4t A")
    dialog.second_start.setDate(QDate(2026, 1, 8))
    dialog.third_start.setDate(QDate(2026, 4, 7))
    assert dialog.values() == {
        "academic_course_id": 3,
        "group_name": "4t A",
        "second_term_start": "2026-01-08",
        "third_term_start": "2026-04-07",
    }
    dialog._accept_valid()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_dialog_configuracio_carrega_valors_existents(qtbot):
    configuration = TermConfiguration(1, 3, "4t B", "2026-01-09", "2026-04-08")
    dialog = TermConfigurationDialog(
        [AcademicCourse(3, "2025-2026")], ["4t A", "4t B"], configuration
    )
    qtbot.addWidget(dialog)
    assert dialog.group_input.currentText() == "4t B"
    assert dialog.values()["third_term_start"] == "2026-04-08"


def test_dialog_exportacio_permet_reordenar_i_ometre_opcio_trimestres(qtbot):
    dialog = ReportExportDialog(
        [Category(1, "Acadèmic"), Category(2, "Família")],
        show_term_option=False,
    )
    qtbot.addWidget(dialog)
    item = dialog.category_list.takeItem(1)
    dialog.category_list.insertItem(0, item)
    assert dialog.category_order() == [2, 1]
    assert dialog.include_terms.isHidden()
    assert dialog.export_format() == "xlsx"
    assert not dialog.include_documents.isChecked()
    dialog.format_input.setCurrentIndex(1)
    assert dialog.export_format() == "docx"
    dialog.format_input.setCurrentIndex(2)
    assert dialog.export_format() == "odt"
    assert not dialog.include_terms.isEnabled()
    dialog.format_input.setCurrentIndex(3)
    assert dialog.export_format() == "pdf"


def test_vista_de_dades_emet_ids_de_configuracio(qtbot):
    view = DataToolsView()
    qtbot.addWidget(view)
    view.set_term_configurations([(7, ("2025-2026", "4t A", "08/01/2026", "07/04/2026"))])
    view.term_table.selectRow(0)
    assert view.current_term_configuration_id() == 7
    assert view.term_edit_button.isEnabled()
    with qtbot.waitSignal(view.term_delete_requested) as signal:
        qtbot.mouseClick(view.term_delete_button, Qt.MouseButton.LeftButton)
    assert signal.args == [7]
    header = view.term_table.horizontalHeader()
    assert header.sectionResizeMode(2) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(3) == QHeaderView.ResizeMode.Stretch
    original_height = view.term_table.maximumHeight()
    view.resize(900, 700)
    view.show()
    qtbot.waitExposed(view)
    assert header.sectionSize(2) == header.sectionSize(3)
    assert header.height() >= header.fontMetrics().lineSpacing() * 2
    assert view.term_table.horizontalHeaderItem(2).text() == "Inici 2n\ntrimestre"
    assert view.term_table.horizontalHeaderItem(3).text() == "Inici 3r\ntrimestre"
    assert view.term_table.maximumHeight() == original_height == 190


def test_vista_de_dades_separa_visualment_les_configuracions(qtbot):
    view = DataToolsView()
    qtbot.addWidget(view)
    groups = view.report_panel.findChildren(QFrame, "settingsGroup")
    assert len(groups) == 3
    titles = [
        label.text() for label in view.report_panel.findChildren(QLabel, "settingsTitle")
    ]
    assert titles == [
        "Ordre de les categories",
        "Logotip dels informes",
        "Configuració de trimestres",
    ]
    buttons = (
        view.category_order_button, view.report_logo_button,
        view.report_logo_remove_button, view.term_create_button,
        view.term_edit_button, view.term_delete_button,
    )
    assert all(button.minimumHeight() == 38 for button in buttons)
    assert all(
        button.sizePolicy().verticalPolicy().name == "Fixed" for button in buttons
    )


def test_capcalera_emet_exportacio_per_alumne_seleccionat(qtbot):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    panel.current_student_id = 12
    with qtbot.waitSignal(panel.export_requested) as signal:
        qtbot.mouseClick(panel.export_button, Qt.MouseButton.LeftButton)
    assert signal.args == [12]
