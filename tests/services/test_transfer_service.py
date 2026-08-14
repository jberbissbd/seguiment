import json
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from tutopy.application import create_services
from tutopy.database.database import Database
from tutopy.models.messaging import (
    CategoryNew, ContactNew, NoteNew, StudentAnnotationNew, StudentNew,
)
from tutopy.models.transfer import (
    TransferAction, TransferDecision,
)
from tutopy.services.exceptions import (
    TransferAuthenticationError, TransferFormatError, ValidationError,
)


PASSWORD = "contrasenya-segura"


@pytest.fixture
def instances(tmp_path):
    source_db = Database(str(tmp_path / "source.db")).connect()
    target_db = Database(str(tmp_path / "target.db")).connect()
    source = create_services(source_db)
    target = create_services(target_db)
    source.documents.storage_dir = tmp_path / "source-documents"
    target.documents.storage_dir = tmp_path / "target-documents"
    try:
        yield source, target
    finally:
        source_db.close()
        target_db.close()


def _complete_student(services, tmp_path, name="Laia"):
    student = services.students.create(StudentNew(name, "Martí", "4t A"))
    category = services.categories.create(CategoryNew("Acadèmic"))
    services.notes.create(NoteNew(
        student.id, category.id, "2026-02-01", 0, "Bona evolució"
    ))
    services.contacts.create(ContactNew(
        student.id, "Marta", "Mare", "600000000", "marta@example.cat"
    ))
    services.annotations.create(StudentAnnotationNew(
        student.id, "Necessita suport visual"
    ))
    source_file = tmp_path / f"{name}.pdf"
    source_file.write_bytes(b"%PDF-document-transfer")
    services.documents.import_file(
        student.id, "Informe", "Valoració", str(source_file), "2026-02-02"
    )
    return student


def test_round_trip_conserva_agregat_i_documents(instances, tmp_path):
    source, target = instances
    original = _complete_student(source, tmp_path)
    package = source.transfers.export_student(
        original.id, tmp_path / "alumne", PASSWORD
    )

    preview = target.transfers.analyze(package, PASSWORD)
    result = target.transfers.execute(preview, password=PASSWORD)

    imported = target.students.get_by_uuid(original.uuid)
    assert package.suffix == ".tpy"
    assert preview.student_count == 1
    assert preview.note_count == 1
    assert preview.document_count == 1
    assert result.created == 1
    assert imported.name == "Laia"
    assert target.notes.get_by_student(imported.id)[0].content == "Bona evolució"
    assert target.contacts.get_by_student(imported.id)[0].email == "marta@example.cat"
    assert target.annotations.get_by_student(imported.id)[0].content.startswith("Necessita")
    assert len(target.students.get_group_history(imported.id)) == 1
    document = target.documents.get_by_student(imported.id)[0]
    assert target.documents.get_readable_path(document.id).read_bytes() == (
        b"%PDF-document-transfer"
    )


def test_exporta_i_importa_tots_els_alumnes(instances, tmp_path):
    source, target = instances
    first = _complete_student(source, tmp_path, "Laia")
    second = source.students.create(StudentNew("Pau", "Puig", "3r B"))

    package = source.transfers.export_all(tmp_path / "tots.tpy", PASSWORD)
    preview = target.transfers.analyze(package, PASSWORD)
    result = target.transfers.execute(preview, password=PASSWORD)

    assert preview.student_count == 2
    assert result.created == 2
    assert {item.uuid for item in target.students.get_all()} == {
        first.uuid, second.uuid,
    }


@pytest.mark.parametrize(
    ("action", "expected_count", "same_uuid"),
    [
        (TransferAction.KEEP_LOCAL, 1, True),
        (TransferAction.REPLACE, 1, True),
        (TransferAction.IMPORT_AS_NEW, 2, True),
    ],
)
def test_conflictes_apliquen_les_tres_decisions(
    instances, tmp_path, action, expected_count, same_uuid
):
    source, target = instances
    original = _complete_student(source, tmp_path)
    package = source.transfers.export_student(
        original.id, tmp_path / "alumne", PASSWORD
    )
    first_preview = target.transfers.analyze(package, PASSWORD)
    target.transfers.execute(first_preview, password=PASSWORD)
    local = target.students.get_by_uuid(original.uuid)
    local.name = "Nom local"
    target.students.update(local)

    preview = target.transfers.analyze(package, PASSWORD)
    result = target.transfers.execute(preview, (
        TransferDecision(original.uuid, action),
    ), password=PASSWORD)

    students = target.students.get_all()
    assert len(students) == expected_count
    assert target.students.get_by_uuid(original.uuid) is not None
    if action == TransferAction.KEEP_LOCAL:
        assert target.students.get_by_uuid(original.uuid).name == "Nom local"
        assert result.skipped == 1
    elif action == TransferAction.REPLACE:
        assert target.students.get_by_uuid(original.uuid).name == "Laia"
        assert result.replaced == 1
    else:
        assert {item.name for item in students} == {"Nom local", "Laia"}
        assert result.imported_as_new == 1


def test_conflicte_exigeix_decisio(instances, tmp_path):
    source, target = instances
    student = _complete_student(source, tmp_path)
    package = source.transfers.export_student(
        student.id, tmp_path / "alumne", PASSWORD
    )
    target.transfers.execute(
        target.transfers.analyze(package, PASSWORD), password=PASSWORD
    )
    preview = target.transfers.analyze(package, PASSWORD)

    with pytest.raises(ValidationError, match="Falten decisions"):
        target.transfers.execute(preview, password=PASSWORD)


def test_rebutja_versio_incompatible_i_rutes_insegures(instances, tmp_path):
    _source, target = instances
    plain = tmp_path / "invalid.zip"
    package = tmp_path / "invalid.tpy"
    with ZipFile(plain, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("../secret.txt", "secret")
        archive.writestr("manifest.json", json.dumps({
            "format": "tutopy-transfer", "format_version": 99,
        }))
        archive.writestr("data.json", json.dumps({"students": []}))
        archive.writestr("checksums.json", "{}")
    target.transfers._encrypt_file(plain, package, PASSWORD)

    with pytest.raises(ValidationError, match="ruta no segura"):
        target.transfers.analyze(package, PASSWORD)


def test_rebutja_document_manipulat(instances, tmp_path):
    source, target = instances
    student = _complete_student(source, tmp_path)
    original = source.transfers.export_student(
        student.id, tmp_path / "original", PASSWORD
    )
    manipulated = tmp_path / "manipulat.tpy"
    content = bytearray(original.read_bytes())
    content[len(content) // 2] ^= 1
    manipulated.write_bytes(content)

    with pytest.raises(TransferAuthenticationError, match="manipulat"):
        target.transfers.analyze(manipulated, PASSWORD)


def test_xifra_tot_el_contingut_i_rebutja_contrasenya_incorrecta(
    instances, tmp_path
):
    source, target = instances
    student = _complete_student(source, tmp_path)
    package = source.transfers.export_student(
        student.id, tmp_path / "alumne", PASSWORD
    )

    raw = package.read_bytes()
    assert raw.startswith(source.transfers.ENVELOPE_MAGIC)
    assert b"Laia" not in raw
    assert b"manifest.json" not in raw
    with pytest.raises(TransferAuthenticationError, match="incorrecta"):
        target.transfers.analyze(package, "contrasenya-erronia")


def test_rebutja_paquets_en_clar_i_contrasenyes_massa_curtes(
    instances, tmp_path
):
    source, target = instances
    plain = tmp_path / "antic.tpy"
    with ZipFile(plain, "w") as archive:
        archive.writestr("manifest.json", "{}")

    with pytest.raises(TransferFormatError, match="xifrat compatible"):
        target.transfers.analyze(plain, PASSWORD)
    with pytest.raises(ValidationError, match="8 caràcters"):
        source.transfers.export_all(tmp_path / "curt.tpy", "curta")


def test_error_durant_documents_fa_rollback_i_neteja_fitxers(
    instances, tmp_path, monkeypatch
):
    source, target = instances
    student = _complete_student(source, tmp_path)
    second_file = tmp_path / "segon.pdf"
    second_file.write_bytes(b"segon document")
    source.documents.import_file(
        student.id, "Segon", "Annex", str(second_file), "2026-03-02"
    )
    package = source.transfers.export_student(
        student.id, tmp_path / "alumne", PASSWORD
    )
    preview = target.transfers.analyze(package, PASSWORD)
    original_import = target.documents.import_file
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValidationError("error simulat al segon document")
        return original_import(*args, **kwargs)

    monkeypatch.setattr(target.documents, "import_file", fail_second)
    with pytest.raises(ValidationError, match="segon document"):
        target.transfers.execute(preview, password=PASSWORD)

    assert target.students.get_all() == []
    assert not target.documents.storage_dir.exists() or not any(
        target.documents.storage_dir.iterdir()
    )
