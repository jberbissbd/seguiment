"""Controlador de la distribució de taules d'aula.

És l'únic punt que modifica el `LayoutGrid` en memòria; els widgets només
emeten senyals i mai el toquen directament. Cada acció de l'usuari
actualitza només les cel·les afectades, no reconstrueix tota la graella
(l'excepció és un canvi de mides, que sí que l'obliga).
"""

import dataclasses

from PySide6.QtWidgets import QDialog, QMessageBox

from tutopy.models.classroom_layout import CellType, ClassroomLayoutNew
from tutopy.models.messaging import Student
from tutopy.services.exceptions import DomainError
from tutopy.services.classroom_layout_service import ClassroomLayoutService
from tutopy.services.photo_service import PhotoService
from tutopy.services.student_service import StudentService
from tutopy.ui.dialogs.classroom_layout_dialog import ClassroomLayoutDialog
from tutopy.ui.widgets import classroom_layout_mime as mime
from tutopy.ui.main_window import MainWindow

TEACHER_WIDTH = 2


class ClassroomLayoutController:
    """Gestiona la distribució de taules d'aula entre la vista i els serveis."""

    def __init__(self, window: MainWindow, service: ClassroomLayoutService,
        students: StudentService, photos: PhotoService = None,
        dialog_factory=ClassroomLayoutDialog, error_handler=None):
        """Desa les dependències i connecta les accions de la vista."""
        self.window = window
        self.service = service
        self.students = students
        self.photos = photos
        self.dialog_factory = dialog_factory
        self.error_handler = error_handler or window.show_error
        self._started = False
        window.sidebar.section_changed.connect(self._section_changed)
        self.group_name: str | None = None
        self.layout = None
        self.grid = None
        self.pending = []
        self.teacher_mode = "strip"
        self.teacher_position = "center"
        self.show_photos = False
        self.dirty = False
        self._students_by_id: dict[int, Student] = {}
        self._connect_signals()

    def _connect_signals(self) -> None:
        view = self.window.classroom_layout_view
        view.group_changed.connect(self.select_group)
        view.layout_selected.connect(self.select_layout)
        view.new_layout_requested.connect(self.new_layout)
        view.rows_columns_changed.connect(self.resize)
        view.teacher_mode_changed.connect(self.change_teacher_mode)
        view.teacher_position_changed.connect(self.change_teacher_position)
        view.show_photos_toggled.connect(self.toggle_show_photos)
        view.save_requested.connect(self.save)
        view.set_active_requested.connect(self.set_active)
        grid = view.grid_widget
        grid.move_requested.connect(self.move_student)
        grid.type_change_requested.connect(self.change_cell_type)
        grid.teacher_place_requested.connect(self.place_teacher)
        grid.return_to_pending_requested.connect(self.return_to_pending)
        view.pending_list.move_requested.connect(self.move_student)

    def _section_changed(self, section: str) -> None:
        """Carrega els grups disponibles la primera vegada que s'obre la secció.

        A diferència de `StatisticsController` (una vista de només lectura
        que es refresca cada cop que s'hi torna), aquí NO es recarrega en
        cada visita: la secció pot tenir canvis sense desar a la graella en
        memòria, i recarregar-los des de la base de dades els perdria en
        silenci.
        """
        if section != "classroom" or self._started:
            return
        self._started = True
        groups = self.students.get_groups()
        self.window.classroom_layout_view.set_groups(groups)
        if groups:
            self.select_group(groups[0])

    def select_group(self, group_name: str) -> None:
        """Carrega les distribucions del grup indicat i n'activa una."""
        if not self._confirm_discard():
            self.window.classroom_layout_view.set_current_group(self.group_name)
            return
        self.group_name = group_name
        self._students_by_id = {student.id: student for student in self.students.get_all()}
        layouts = self._refresh_layouts_list()
        if layouts:
            active = next((layout for layout in layouts if layout.is_active), layouts[0])
            self.select_layout(active.id)
        else:
            self.layout = self.grid = None
            self.pending = []
            self.dirty = False

    def _refresh_layouts_list(self) -> list:
        layouts = self.service.get_layouts(self.group_name) if self.group_name else []
        current_id = self.layout.id if self.layout else None
        self.window.classroom_layout_view.set_layouts(
            [(layout.id, layout.name, layout.is_active) for layout in layouts], current_id,
        )
        return layouts

    def select_layout(self, layout_id: int) -> None:
        """Carrega una distribució existent i en refresca la vista."""
        if not self._confirm_discard():
            self._refresh_layouts_list()
            return
        try:
            self.layout, self.grid, self.pending = self.service.load(layout_id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.teacher_mode = self.layout.teacher_mode
        self.teacher_position = self.layout.teacher_position
        self.show_photos = self.layout.show_photos
        self.dirty = False
        self._refresh_all()

    def new_layout(self) -> None:
        """Obre el diàleg de nova distribució i la selecciona si es crea."""
        if not self.group_name:
            self.error_handler("Selecciona primer un grup.")
            return
        dialog = self.dialog_factory(self.group_name, self.window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            layout = self.service.create_layout(ClassroomLayoutNew(**dialog.values()))
        except DomainError as error:
            self.error_handler(str(error))
            return
        self._refresh_layouts_list()
        self.select_layout(layout.id)

    def move_student(self, student_id: int, origin: str, row: int, column: int) -> None:
        """Assigna un alumne a `(row, column)`, intercanviant-lo o traient-lo de pendents."""
        if self.grid is None:
            return
        displaced = self.grid.assign(student_id, row, column)
        origin_cell = mime.parse_cell_origin(origin)
        if origin_cell is not None:
            if displaced is not None:
                self.grid.assign(displaced, *origin_cell)
                self._update_cell(*origin_cell)
        else:
            self.pending = [student for student in self.pending if student.id != student_id]
            if displaced is not None:
                displaced_student = self._student_by_id(displaced)
                if displaced_student is not None:
                    self.pending.append(displaced_student)
        self._mark_dirty()
        self._update_cell(row, column)
        self._refresh_pending()

    def return_to_pending(self, student_id: int) -> None:
        """Treu un alumne de la seva cel·la i el torna a la llista de pendents."""
        if self.grid is None:
            return
        cell = self.grid.remove(student_id)
        if cell is None:
            return
        student = self._student_by_id(student_id)
        if student is not None:
            self.pending.append(student)
        self._mark_dirty()
        self._update_cell(cell.row, cell.column)
        self._refresh_pending()

    def change_cell_type(self, row: int, column: int, cell_type_value: str) -> None:
        """Canvia el tipus d'una cel·la, tornant a pendents l'alumne desplaçat."""
        if self.grid is None:
            return
        displaced = self.grid.set_cell_type(row, column, CellType(cell_type_value))
        if displaced is not None:
            student = self._student_by_id(displaced)
            if student is not None:
                self.pending.append(student)
        self._mark_dirty()
        self._update_cell(row, column)
        self._refresh_pending()

    def resize(self, rows: int, columns: int) -> None:
        """Redimensiona la graella, tornant a pendents els alumnes que en queden fora."""
        if self.grid is None:
            return
        displaced = self.grid.resize(rows, columns)
        for student_id in displaced:
            student = self._student_by_id(student_id)
            if student is not None:
                self.pending.append(student)
        self._mark_dirty()
        self._refresh_all()

    def place_teacher(self, row: int, column: int) -> None:
        """Col·loca la taula del professor dins la graella, a `(row, column)`."""
        if self.grid is None:
            return
        self.teacher_mode = "grid"
        displaced = self.grid.place_teacher(row, column, TEACHER_WIDTH)
        for student_id in displaced:
            student = self._student_by_id(student_id)
            if student is not None:
                self.pending.append(student)
        self._mark_dirty()
        self._refresh_all()

    def change_teacher_mode(self, mode: str) -> None:
        """Canvia entre taula en franja o dins la graella."""
        if self.grid is None or mode == self.teacher_mode:
            return
        self.teacher_mode = mode
        if mode == "strip":
            for (row, column), cell in list(self.grid.cells.items()):
                if cell.cell_type == CellType.TEACHER:
                    self.grid.set_cell_type(row, column, CellType.SEAT)
        self._mark_dirty()
        self._refresh_all()

    def change_teacher_position(self, position: str) -> None:
        """Canvia l'alineació de la franja del professor."""
        self.teacher_position = position
        self._mark_dirty()
        self.window.classroom_layout_view.set_teacher_strip(
            self.teacher_mode == "strip", position,
        )

    def toggle_show_photos(self, enabled: bool) -> None:
        """Activa o desactiva mostrar la foto de l'alumne en lloc de les inicials."""
        self.show_photos = enabled
        self._mark_dirty()
        self._refresh_all()

    def save(self) -> None:
        """Desa la distribució actual."""
        if self.layout is None or self.grid is None:
            return
        updated = dataclasses.replace(
            self.layout, teacher_mode=self.teacher_mode,
            teacher_position=self.teacher_position, show_photos=self.show_photos,
        )
        try:
            self.layout = self.service.save(updated, self.grid)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.dirty = False
        self.window.classroom_layout_view.set_dirty(False)
        self.window.show_status("Distribució desada")

    def set_active(self) -> None:
        """Marca la distribució actual com l'activa del seu grup."""
        if self.layout is None:
            return
        try:
            self.service.set_active(self.layout.id)
        except DomainError as error:
            self.error_handler(str(error))
            return
        self.select_group(self.group_name)
        self.window.show_status("Distribució marcada com a activa")

    def _mark_dirty(self) -> None:
        self.dirty = True
        self.window.classroom_layout_view.set_dirty(True)

    def _student_by_id(self, student_id: int) -> Student | None:
        return self._students_by_id.get(student_id)

    def _photo_paths(self, student_ids) -> dict:
        if not self.photos or not self.show_photos or not student_ids:
            return {}
        paths = self.photos.get_readable_paths(list(student_ids))
        return {student_id: str(path) if path else None for student_id, path in paths.items()}

    def _refresh_all(self) -> None:
        view = self.window.classroom_layout_view
        if self.layout is None or self.grid is None:
            return
        view.set_layout_fields(
            self.grid.rows, self.grid.columns, self.teacher_mode,
            self.teacher_position, self.show_photos,
        )
        assigned = self.grid.assigned()
        students_by_id = {
            student_id: self._student_by_id(student_id) for student_id in assigned
        }
        photo_paths = self._photo_paths(assigned.keys())
        view.grid_widget.rebuild(self.grid, students_by_id, self.show_photos, photo_paths)
        view.set_dirty(self.dirty)
        self._refresh_pending()

    def _refresh_pending(self) -> None:
        view = self.window.classroom_layout_view
        photo_paths = self._photo_paths([student.id for student in self.pending])
        view.pending_list.set_students(self.pending, self.show_photos, photo_paths)

    def _update_cell(self, row: int, column: int) -> None:
        if self.grid is None:
            return
        cell = self.grid.cells.get((row, column))
        if cell is None:
            return
        student = self._student_by_id(cell.student_id) if cell.student_id else None
        photo_path = self._photo_paths([cell.student_id]).get(cell.student_id) \
            if cell.student_id else None
        self.window.classroom_layout_view.grid_widget.update_cell(
            row, column, cell.cell_type, student, photo_path, self.show_photos,
        )

    def _confirm_discard(self) -> bool:
        if not self.dirty:
            return True
        box = QMessageBox(self.window)
        box.setWindowTitle("Canvis sense desar")
        box.setText("Hi ha canvis sense desar en aquesta distribució. Què vols fer-ne?")
        save_button = box.addButton("Desar", QMessageBox.ButtonRole.AcceptRole)
        discard_button = box.addButton("Descartar", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Cancel·lar", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is save_button:
            self.save()
            return True
        if clicked is discard_button:
            self.dirty = False
            return True
        return False
