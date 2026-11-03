"""Servei de gestió de les distribucions de taules d'aula."""

import dataclasses
from datetime import datetime
from typing import Optional

from tutopy.database.daos.classroom_layout_dao import ClassroomLayoutDAO
from tutopy.database.daos.student_dao import StudentDAO
from tutopy.models.classroom_layout import ClassroomLayout, ClassroomLayoutNew, LayoutGrid
from tutopy.models.messaging import Student
from tutopy.services.exceptions import EntityNotFoundError, ValidationError
from tutopy.services.validation_service import ValidationService

MIN_SIZE = 1
MAX_SIZE = 20
TEACHER_MODES = ("strip", "grid")
TEACHER_POSITIONS = ("left", "center", "right")


class ClassroomLayoutService:
    """Gestiona el cicle de vida de les distribucions de taules d'aula."""

    def __init__(self, layout_dao: ClassroomLayoutDAO, student_dao: StudentDAO,
        transaction_factory, validation_service: ValidationService = None):
        """Injecta els DAOs i la factoria de transaccions."""
        self.layout_dao = layout_dao
        self.student_dao = student_dao
        self.transaction_factory = transaction_factory
        self.validation_service = validation_service or ValidationService()

    def get_layouts(self, group_name: str) -> list[ClassroomLayout]:
        """Retorna totes les distribucions d'un grup."""
        group_name = self.validation_service.required_text(
            group_name, "El grup no pot estar buit."
        )
        return self.layout_dao.get_by_group(group_name)

    def get_active(self, group_name: str) -> Optional[ClassroomLayout]:
        """Retorna la distribució activa d'un grup, o `None` si no n'hi ha cap."""
        return self.layout_dao.get_active(group_name)

    def create_layout(self, data: ClassroomLayoutNew) -> ClassroomLayout:
        """Valida i crea una nova distribució buida."""
        data = self._validate(data)
        with self.transaction_factory():
            layout = self.layout_dao.create(data, self._today())
        return layout

    def load(self, layout_id: int) -> tuple[ClassroomLayout, LayoutGrid, list[Student]]:
        """Carrega una distribució, la seva graella i els alumnes pendents.

        Si una cel·la té assignat un alumne que ja no pertany al grup de la
        distribució, es buida (l'alumne haurà canviat de grup després de
        col·locar-lo).

        Returns:
            La distribució, la seva graella i la llista d'alumnes del grup
            que no apareixen a cap cel·la, ordenats com ja fa
            `StudentDAO.get_all` (cognoms, nom).
        """
        layout = self._require_layout(layout_id)
        group_students = [
            student for student in self.student_dao.get_all()
            if student.group_name == layout.group_name
        ]
        group_ids = {student.id for student in group_students}
        cells = self.layout_dao.get_cells(layout_id)
        grid = LayoutGrid(layout.rows, layout.columns)
        for cell in cells:
            student_id = cell.student_id if cell.student_id in group_ids else None
            grid.cells[(cell.row, cell.column)] = dataclasses.replace(
                cell, student_id=student_id,
            )
        assigned_ids = set(grid.assigned())
        pending = [student for student in group_students if student.id not in assigned_ids]
        return layout, grid, pending

    def save(self, layout: ClassroomLayout, grid: LayoutGrid) -> ClassroomLayout:
        """Desa les metadades i substitueix totes les cel·les de la distribució."""
        updated = dataclasses.replace(layout, rows=grid.rows, columns=grid.columns)
        with self.transaction_factory():
            self.layout_dao.update(updated, self._today())
            self.layout_dao.replace_cells(layout.id, list(grid.cells.values()))
        return self.layout_dao.get_by_id(layout.id)

    def get_shape(self, layout_id: int) -> LayoutGrid:
        """Retorna la forma (cel·les, sense alumnes) d'una distribució existent.

        Útil per aplicar la disposició "Duplicar una existent" com a
        plantilla sense crear encara cap registre nou (a diferència de
        `duplicate`, que sí que en desa una còpia immediatament).
        """
        layout = self._require_layout(layout_id)
        cells = self.layout_dao.get_cells(layout_id)
        grid = LayoutGrid(layout.rows, layout.columns)
        for cell in cells:
            grid.cells[(cell.row, cell.column)] = dataclasses.replace(cell, student_id=None)
        return grid

    def duplicate(self, layout_id: int, new_name: str) -> ClassroomLayout:
        """Crea una còpia de la forma d'una distribució, sense els alumnes assignats.

        Útil com a punt de partida per retocar-la sense alterar l'original.
        """
        source = self._require_layout(layout_id)
        new_name = self.validation_service.required_text(
            new_name, "El nom de la distribució no pot estar buit."
        )
        source_cells = self.layout_dao.get_cells(layout_id)
        with self.transaction_factory():
            new_layout = self.layout_dao.create(
                ClassroomLayoutNew(
                    source.group_name, new_name, source.rows, source.columns,
                    source.teacher_mode, source.teacher_position, source.show_photos,
                ),
                self._today(),
            )
            copied_cells = [
                dataclasses.replace(cell, student_id=None) for cell in source_cells
            ]
            self.layout_dao.replace_cells(new_layout.id, copied_cells)
        return self.layout_dao.get_by_id(new_layout.id)

    def set_active(self, layout_id: int) -> None:
        """Marca una distribució com l'activa del seu grup."""
        layout = self._require_layout(layout_id)
        with self.transaction_factory():
            self.layout_dao.set_active(layout_id, layout.group_name)

    def delete(self, layout_id: int) -> None:
        """Elimina una distribució existent."""
        self._require_layout(layout_id)
        with self.transaction_factory():
            self.layout_dao.delete(layout_id)

    def _require_layout(self, layout_id: int) -> ClassroomLayout:
        self.validation_service.positive_id(layout_id)
        layout = self.layout_dao.get_by_id(layout_id)
        if layout is None:
            raise EntityNotFoundError(f"La distribució amb ID {layout_id} no existeix.")
        return layout

    def _validate(self, data: ClassroomLayoutNew) -> ClassroomLayoutNew:
        group_name = self.validation_service.required_text(
            data.group_name, "El grup no pot estar buit."
        )
        name = self.validation_service.required_text(
            data.name, "El nom de la distribució no pot estar buit."
        )
        for label, value in (("files", data.rows), ("columnes", data.columns)):
            if not isinstance(value, int) or isinstance(value, bool) or not (
                MIN_SIZE <= value <= MAX_SIZE
            ):
                raise ValidationError(
                    f"El nombre de {label} ha de ser entre {MIN_SIZE} i {MAX_SIZE}."
                )
        if data.teacher_mode not in TEACHER_MODES:
            raise ValidationError("El mode de la taula del professor no és vàlid.")
        if data.teacher_position not in TEACHER_POSITIONS:
            raise ValidationError("La posició de la taula del professor no és vàlida.")
        return ClassroomLayoutNew(
            group_name, name, data.rows, data.columns, data.teacher_mode,
            data.teacher_position, data.show_photos,
        )

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%Y-%m-%d")
