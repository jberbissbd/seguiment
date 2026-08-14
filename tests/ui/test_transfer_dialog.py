from tutopy.models.transfer import TransferAction, TransferConflict
from tutopy.ui.dialogs.transfer_conflicts_dialog import TransferConflictsDialog


def test_dialog_transferencia_retorna_una_decisio_per_conflicte(qtbot):
    conflicts = (
        TransferConflict("uuid-1", "Martí, Laia", "Martí, Laia local"),
        TransferConflict("uuid-2", "Puig, Pau", "Puig, Pau local"),
    )
    dialog = TransferConflictsDialog(conflicts)
    qtbot.addWidget(dialog)
    dialog.table.cellWidget(0, 2).setCurrentIndex(1)
    dialog.table.cellWidget(1, 2).setCurrentIndex(2)

    decisions = dialog.decisions()

    assert decisions[0].uuid == "uuid-1"
    assert decisions[0].action == TransferAction.REPLACE
    assert decisions[1].action == TransferAction.IMPORT_AS_NEW
