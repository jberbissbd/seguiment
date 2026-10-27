from pathlib import Path

import pytest

from tutopy.models.messaging import StudentNew
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.photo_service import PhotoService
from .conftest import MINIMAL_PNG


def test_set_photo_copia_i_substitueix_l_anterior(managed_photo, tmp_path):
    """set_photo substitueix la foto anterior i n'esborra el fitxer gestionat."""
    service, photo, _source = managed_photo
    previous_path = Path(photo.file_path)
    assert previous_path.is_file()

    new_source = tmp_path / "nova.png"
    new_source.write_bytes(MINIMAL_PNG)
    updated = service.set_photo(photo.student_id, str(new_source))

    assert updated.file_path != photo.file_path
    assert Path(updated.file_path).is_file()
    assert not previous_path.exists()
    assert service.get_by_student(photo.student_id) == updated


def test_set_photo_rebutja_fitxer_que_no_es_imatge(managed_photo, tmp_path):
    """set_photo rebutja un fitxer que no és una imatge vàlida."""
    service, photo, _source = managed_photo
    not_an_image = tmp_path / "document.txt"
    not_an_image.write_text("això no és una imatge")
    with pytest.raises(ValidationError, match="imatge"):
        service.set_photo(photo.student_id, str(not_an_image))
    assert service.get_by_student(photo.student_id) == photo


@pytest.mark.parametrize("failure", ["storage", "source"])
def test_set_photo_rebutja_magatzem_o_origen_absents(managed_photo, failure):
    """Els requisits absents no creen ni alteren el registre de la foto."""
    service, photo, source = managed_photo
    if failure == "storage":
        service.storage_dir = None
    else:
        source.unlink()
    with pytest.raises(ValidationError, match="directori|no existeix"):
        service.set_photo(photo.student_id, str(source))
    if failure == "source":
        assert service.get_by_student(photo.student_id) == photo


def test_set_photo_alumne_inexistent(db, tmp_path):
    """set_photo rebutja un identificador d'alumne que no existeix."""
    service = PhotoService(db.photos, db.students, storage_dir=tmp_path / "managed")
    source = tmp_path / "foto.png"
    source.write_bytes(MINIMAL_PNG)
    with pytest.raises(EntityNotFoundError):
        service.set_photo(999, str(source))


def test_remove_photo_elimina_registre_i_fitxer(managed_photo):
    """remove_photo esborra tant el registre com el fitxer gestionat."""
    service, photo, _source = managed_photo
    service.remove_photo(photo.student_id)
    assert service.get_by_student(photo.student_id) is None
    assert not Path(photo.file_path).exists()


def test_remove_photo_sense_foto_no_falla(db, tmp_path):
    """remove_photo és segur de cridar encara que l'alumne no tingui foto."""
    student = db.students.create(StudentNew("Pau", "Font", "3B"))
    service = PhotoService(db.photos, db.students, storage_dir=tmp_path / "managed")
    service.remove_photo(student.id)
    assert service.get_by_student(student.id) is None


def test_get_readable_path_none_si_no_hi_ha_foto(db, tmp_path):
    """get_readable_path retorna None si l'alumne no té cap foto."""
    student = db.students.create(StudentNew("Pau", "Font", "3B"))
    service = PhotoService(db.photos, db.students, storage_dir=tmp_path / "managed")
    assert service.get_readable_path(student.id) is None


def test_get_readable_paths_per_lots(managed_photo, db):
    """get_readable_paths resol la ruta de diversos alumnes alhora."""
    service, photo, _source = managed_photo
    sense_foto = db.students.create(StudentNew("Pau", "Font", "3B"))
    paths = service.get_readable_paths([photo.student_id, sense_foto.id])
    assert paths[photo.student_id] == Path(photo.file_path)
    assert paths[sense_foto.id] is None
