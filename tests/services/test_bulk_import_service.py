from openpyxl import load_workbook

from tutopy.application import create_services
from tutopy.models.bulk_import import ImportAction, ImportDecision
from tutopy.models.messaging import CategoryNew, StudentNew


def _filled_template(service, path, students=(), categories=()):
    service.create_template(path)
    workbook = load_workbook(path)
    for row in students:
        workbook["Alumnes"].append(row)
    for row in categories:
        workbook["Categories"].append(row)
    workbook.save(path)


def test_template_te_els_fulls_i_capcaleres(db, tmp_path):
    service = create_services(db).bulk_import
    path = service.create_template(tmp_path / "plantilla")
    workbook = load_workbook(path, read_only=True)
    assert workbook.sheetnames == ["Instruccions", "Alumnes", "Categories"]
    assert tuple(cell.value for cell in workbook["Alumnes"][1]) == ("Nom", "Cognoms", "Grup")
    assert tuple(cell.value for cell in workbook["Categories"][1]) == ("Nom",)


def test_analyze_indica_full_fila_i_motiu(db, tmp_path):
    service = create_services(db).bulk_import
    path = tmp_path / "dades.xlsx"
    _filled_template(service, path, students=[("Anna", "Serra", "1r A"), (None, "Puig", "1r B")])
    preview = service.analyze(path)
    assert [str(issue) for issue in preview.issues] == [
        "Alumnes — fila 3: el nom és obligatori"
    ]


def test_importa_alumnes_i_reutilitza_categories_exactes(db, tmp_path):
    services = create_services(db)
    services.categories.create(CategoryNew("Acadèmic"))
    path = tmp_path / "dades.xlsx"
    _filled_template(services.bulk_import, path,
                     students=[("Anna", "Serra", "1r A")],
                     categories=[("ACADÈMIC",), ("Família",)])
    result = services.bulk_import.execute(services.bulk_import.analyze(path))
    assert result.students_created == 1
    assert result.categories_created == 1
    assert result.categories_reused == 1
    assert services.students.get_all()[0].group_name == "1r A"


def test_coincidencia_similar_requereix_decisio_i_preserva_uuid(db, tmp_path):
    services = create_services(db)
    existing = services.students.create(StudentNew("Júlia", "Martínez", "2n A"))
    path = tmp_path / "dades.xlsx"
    _filled_template(services.bulk_import, path,
                     students=[("Julia", "Martines", "2n B")])
    preview = services.bulk_import.analyze(path)
    assert preview.conflicts[0].matches[0].id == existing.id
    result = services.bulk_import.execute(preview, (
        ImportDecision(2, ImportAction.UPDATE, existing.id),
    ))
    updated = services.students.get_by_id(existing.id)
    assert result.students_updated == 1
    assert updated.uuid == existing.uuid
    assert updated.group_name == "2n B"


def test_error_durant_execucio_desfa_tota_la_importacio(db, tmp_path):
    services = create_services(db)
    path = tmp_path / "dades.xlsx"
    _filled_template(services.bulk_import, path,
                     students=[("Anna", "Serra", "1r A"), ("Pau", "Puig", "1r B")])
    preview = services.bulk_import.analyze(path)
    original_create = services.students.create
    calls = 0

    def failing_create(data):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("error simulat")
        return original_create(data)

    services.students.create = failing_create
    try:
        import pytest
        with pytest.raises(Exception, match="Alumnes — fila 3: error simulat"):
            services.bulk_import.execute(preview)
    finally:
        services.students.create = original_create
    assert services.students.get_all() == []
