"""Tests de la vista de distribució d'aula."""

from tutopy.ui.widgets.classroom_layout_view import ClassroomLayoutView
from tutopy.ui.widgets.collapsible_splitter import CollapsibleSplitter


def _splitter(view: ClassroomLayoutView) -> CollapsibleSplitter:
    return view.pending_list.parent()


def test_pending_list_es_el_primer_panell_dun_separador_plegable(qtbot):
    """Pending list és el primer panell d'un separador plegable."""
    view = ClassroomLayoutView()
    qtbot.addWidget(view)
    splitter = _splitter(view)
    assert isinstance(splitter, CollapsibleSplitter)
    assert splitter.widget(0) is view.pending_list


def test_toggle_first_panel_redueix_i_restaura_la_llista(qtbot):
    """Toggle first panel redueix i restaura la llista."""
    view = ClassroomLayoutView()
    qtbot.addWidget(view)
    view.resize(800, 600)
    view.show()
    splitter = _splitter(view)
    assert view.pending_list.width() > 0

    splitter.toggle_first_panel()
    assert view.pending_list.width() == 0
    assert splitter.handle(1).isHidden() is False

    splitter.toggle_first_panel()
    assert view.pending_list.width() > 0
