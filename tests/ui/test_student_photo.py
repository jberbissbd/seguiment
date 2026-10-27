from PySide6.QtGui import QColor, QPixmap

from tutopy.models.messaging import Student
from tutopy.ui.widgets.student_detail_panel import StudentDetailPanel
from tutopy.ui.widgets.student_list_view import StudentListModel


def _write_png(tmp_path, name="foto.png"):
    """Genera un PNG vàlid real (via Qt) perquè QPixmap el pugui decodificar."""
    path = tmp_path / name
    pixmap = QPixmap(4, 4)
    pixmap.fill(QColor("red"))
    pixmap.save(str(path), "PNG")
    return path


def test_set_photo_mostra_la_imatge_i_torna_a_les_inicials(qtbot, tmp_path):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    panel.show_student(Student(1, "uuid", "Maria", "Serra", "4t A"))
    assert panel.avatar_value.text() == "MS"

    photo_path = _write_png(tmp_path)
    panel.set_photo(str(photo_path))
    assert not panel.avatar_value.icon().isNull()
    assert panel.avatar_value.text() == ""
    assert panel._has_photo is True

    panel.set_photo(None)
    assert panel.avatar_value.icon().isNull()
    assert panel.avatar_value.text() == "MS"
    assert panel._has_photo is False


def test_set_photo_amb_fitxer_no_imatge_recula_a_inicials(qtbot, tmp_path):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    panel.show_student(Student(1, "uuid", "Maria", "Serra", "4t A"))

    not_an_image = tmp_path / "document.txt"
    not_an_image.write_text("no és una imatge")
    panel.set_photo(str(not_an_image))

    assert panel.avatar_value.text() == "MS"
    assert panel._has_photo is False


def test_clic_a_l_avatar_emet_photo_change_requested(qtbot):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    panel.show_student(Student(7, "uuid", "Pau", "Font", "3B"))

    with qtbot.waitSignal(panel.photo_change_requested) as signal:
        panel.avatar_value.click()
    assert signal.args == [7]


def test_clear_oblida_l_alumne_i_la_foto(qtbot, tmp_path):
    panel = StudentDetailPanel()
    qtbot.addWidget(panel)
    panel.show_student(Student(1, "uuid", "Maria", "Serra", "4t A"))
    panel.set_photo(str(_write_png(tmp_path)))

    panel.clear()
    assert panel.current_student_id is None
    assert panel._has_photo is False


def test_student_list_model_set_photos_i_photo_pixmap(tmp_path):
    model = StudentListModel()
    student = Student(1, "uuid", "Maria", "Serra", "4t A")
    model.set_students([student])

    assert model.photo_pixmap(student.id) is None

    photo_path = str(_write_png(tmp_path))
    model.set_photos({student.id: photo_path})
    index = model.index(0)
    assert index.data(StudentListModel.PhotoRole) == photo_path

    pixmap = model.photo_pixmap(student.id)
    assert pixmap is not None
    assert pixmap is model.photo_pixmap(student.id)  # memoritzat, no es torna a decodificar

    model.set_photos({student.id: None})
    assert model.photo_pixmap(student.id) is None


def test_student_list_model_photo_pixmap_amb_ruta_invalida(tmp_path):
    model = StudentListModel()
    student = Student(1, "uuid", "Maria", "Serra", "4t A")
    model.set_students([student])
    model.set_photos({student.id: str(tmp_path / "no-existeix.png")})
    assert model.photo_pixmap(student.id) is None
