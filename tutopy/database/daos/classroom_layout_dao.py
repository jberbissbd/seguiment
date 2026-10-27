"""DAO per a les distribucions de taules d'aula i les seves cel·les."""

from typing import Optional
from tutopy.models.classroom_layout import CellType, ClassroomLayout, ClassroomLayoutNew, LayoutCell


class ClassroomLayoutDAO:
    """Accés a persistència per a les distribucions d'aula i les seves cel·les."""

    _COLUMNS = (
        "id, group_name, name, rows, columns, teacher_mode, teacher_position, "
        "show_photos, is_active, created_at, updated_at"
    )

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_by_group(self, group_name: str) -> list[ClassroomLayout]:
        """Retorna totes les distribucions d'un grup, ordenades per nom."""
        rows = self.conn.execute(
            f"SELECT {self._COLUMNS} FROM classroom_layouts "
            "WHERE group_name = ? ORDER BY name",
            (group_name,),
        ).fetchall()
        return [self._to_layout(row) for row in rows]

    def get_by_id(self, layout_id: int) -> Optional[ClassroomLayout]:
        """Retorna una distribució pel seu ID, o `None` si no existeix."""
        row = self.conn.execute(
            f"SELECT {self._COLUMNS} FROM classroom_layouts WHERE id = ?",
            (layout_id,),
        ).fetchone()
        return self._to_layout(row) if row else None

    def get_active(self, group_name: str) -> Optional[ClassroomLayout]:
        """Retorna la distribució activa d'un grup, o `None` si no n'hi ha cap."""
        row = self.conn.execute(
            f"SELECT {self._COLUMNS} FROM classroom_layouts "
            "WHERE group_name = ? AND is_active = 1",
            (group_name,),
        ).fetchone()
        return self._to_layout(row) if row else None

    def create(self, data: ClassroomLayoutNew, timestamp: str) -> ClassroomLayout:
        """Crea una nova distribució buida."""
        cur = self.conn.execute(
            "INSERT INTO classroom_layouts "
            "(group_name, name, rows, columns, teacher_mode, teacher_position, "
            "show_photos, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data.group_name, data.name, data.rows, data.columns, data.teacher_mode,
             data.teacher_position, int(data.show_photos), timestamp, timestamp),
        )
        self.conn.commit()
        return self.get_by_id(cur.lastrowid)

    def update(self, layout: ClassroomLayout, timestamp: str) -> None:
        """Actualitza les metadades d'una distribució existent."""
        self.conn.execute(
            "UPDATE classroom_layouts SET name = ?, rows = ?, columns = ?, "
            "teacher_mode = ?, teacher_position = ?, show_photos = ?, updated_at = ? "
            "WHERE id = ?",
            (layout.name, layout.rows, layout.columns, layout.teacher_mode,
             layout.teacher_position, int(layout.show_photos), timestamp, layout.id),
        )
        self.conn.commit()

    def delete(self, layout_id: int) -> None:
        """Elimina una distribució i les seves cel·les (per CASCADE)."""
        self.conn.execute("DELETE FROM classroom_layouts WHERE id = ?", (layout_id,))
        self.conn.commit()

    def set_active(self, layout_id: int, group_name: str) -> None:
        """Marca `layout_id` com a activa, desmarcant qualsevol altra del mateix grup."""
        self.conn.execute(
            "UPDATE classroom_layouts SET is_active = 0 WHERE group_name = ?",
            (group_name,),
        )
        self.conn.execute(
            "UPDATE classroom_layouts SET is_active = 1 WHERE id = ?", (layout_id,),
        )
        self.conn.commit()

    def get_cells(self, layout_id: int) -> list[LayoutCell]:
        """Retorna totes les cel·les d'una distribució."""
        rows = self.conn.execute(
            "SELECT cell_row, cell_column, cell_type, block, student_id "
            "FROM classroom_layout_cells WHERE layout_id = ?",
            (layout_id,),
        ).fetchall()
        return [
            LayoutCell(
                row["cell_row"], row["cell_column"], CellType(row["cell_type"]),
                row["block"], row["student_id"],
            )
            for row in rows
        ]

    def replace_cells(self, layout_id: int, cells: list[LayoutCell]) -> None:
        """Substitueix totes les cel·les d'una distribució (esborra i insereix)."""
        self.conn.execute(
            "DELETE FROM classroom_layout_cells WHERE layout_id = ?", (layout_id,),
        )
        self.conn.executemany(
            "INSERT INTO classroom_layout_cells "
            "(layout_id, cell_row, cell_column, cell_type, block, student_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                (layout_id, cell.row, cell.column, cell.cell_type.value,
                 cell.block, cell.student_id)
                for cell in cells
            ],
        )
        self.conn.commit()

    @staticmethod
    def _to_layout(row) -> ClassroomLayout:
        return ClassroomLayout(
            id=row["id"], group_name=row["group_name"], name=row["name"],
            rows=row["rows"], columns=row["columns"],
            teacher_mode=row["teacher_mode"], teacher_position=row["teacher_position"],
            show_photos=bool(row["show_photos"]), is_active=bool(row["is_active"]),
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
