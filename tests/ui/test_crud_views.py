from tutopy.ui.widgets.crud_views import CrudListView, CrudTableView


def test_crud_list_view_selecciona_edita_i_elimina(qtbot):
    view = CrudListView(create_text="Nou alumne")
    qtbot.addWidget(view)
    created = []
    edited = []
    deleted = []
    view.create_requested.connect(lambda: created.append(True))
    view.edit_requested.connect(edited.append)
    view.delete_requested.connect(deleted.append)

    assert view.current_id() is None
    assert not view.actions.edit_button.isEnabled()
    assert not view.actions.delete_button.isEnabled()

    view.set_items([(1, "Primer"), (2, "Segon")])
    view.list_widget.setCurrentRow(1)

    assert view.current_id() == 2
    assert view.actions.edit_button.isEnabled()
    assert view.actions.delete_button.isEnabled()

    view.actions.create_button.click()
    view.actions.edit_button.click()
    view.actions.delete_button.click()
    view.list_widget.itemDoubleClicked.emit(view.list_widget.item(0))

    assert created == [True]
    assert edited == [2, 1]
    assert deleted == [2]


def test_crud_list_view_conserva_seleccio_en_refer_items(qtbot):
    view = CrudListView()
    qtbot.addWidget(view)
    view.set_items([(1, "Primer"), (2, "Segon")])
    view.list_widget.setCurrentRow(1)

    view.set_items([(1, "Primer"), (2, "Segon (editat)")])

    assert view.current_id() == 2
    assert view.list_widget.currentItem().text() == "Segon (editat)"


def test_crud_list_view_no_emet_sense_seleccio(qtbot):
    view = CrudListView()
    qtbot.addWidget(view)
    edited = []
    deleted = []
    view.edit_requested.connect(edited.append)
    view.delete_requested.connect(deleted.append)

    view._edit()
    view._delete()

    assert edited == []
    assert deleted == []


def test_crud_table_view_selecciona_edita_i_elimina(qtbot):
    view = CrudTableView(headers=("Nom", "Grup"), create_text="Nou alumne")
    qtbot.addWidget(view)
    created = []
    edited = []
    deleted = []
    view.create_requested.connect(lambda: created.append(True))
    view.edit_requested.connect(edited.append)
    view.delete_requested.connect(deleted.append)

    assert view.current_id() is None
    assert not view.actions.edit_button.isEnabled()

    view.set_rows([(1, ("Anna", "1A")), (2, ("Biel", "1B"))])
    view.table.selectRow(1)

    assert view.current_id() == 2
    assert view.actions.edit_button.isEnabled()
    assert view.actions.delete_button.isEnabled()

    view.actions.create_button.click()
    view.actions.edit_button.click()
    view.actions.delete_button.click()
    view.table.cellDoubleClicked.emit(0, 0)

    assert created == [True]
    assert edited == [2, 1]
    assert deleted == [2]


def test_crud_table_view_conserva_seleccio_en_refer_files(qtbot):
    view = CrudTableView(headers=("Nom",))
    qtbot.addWidget(view)
    view.set_rows([(1, ("Anna",)), (2, ("Biel",))])
    view.table.selectRow(1)

    view.set_rows([(1, ("Anna",)), (2, ("Biel Actualitzat",))])

    assert view.current_id() == 2
    assert view.table.item(1, 0).text() == "Biel Actualitzat"


def test_crud_table_view_no_emet_sense_seleccio(qtbot):
    view = CrudTableView(headers=("Nom",))
    qtbot.addWidget(view)
    edited = []
    deleted = []
    view.edit_requested.connect(edited.append)
    view.delete_requested.connect(deleted.append)

    view._edit()
    view._delete()

    assert edited == []
    assert deleted == []
