"""DAO per a la foto de perfil dels alumnes."""

from typing import Optional
from tutopy.models.messaging import StudentPhoto
from ._batch import SQLITE_PARAMETER_BATCH


class PhotoDAO:
    """Accés a persistència per a la foto de perfil dels alumnes."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def get_by_student(self, student_id: int) -> Optional[StudentPhoto]:
        """Retorna la foto d'un alumne, o ``None`` si no en té."""
        row = self.conn.execute(
            "SELECT student_id, uuid_filename, original_filename, file_path "
            "FROM student_photos WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        return StudentPhoto(**row) if row else None

    def get_by_students(self, student_ids: list[int]) -> dict[int, Optional[StudentPhoto]]:
        """Retorna la foto de cada alumne indicat, amb lectures per blocs.

        Cada identificador demanat és present al resultat, amb ``None`` si
        l'alumne no té cap foto.
        """
        unique_ids = tuple(dict.fromkeys(student_ids))
        photos: dict[int, Optional[StudentPhoto]] = dict.fromkeys(unique_ids)
        for offset in range(0, len(unique_ids), SQLITE_PARAMETER_BATCH):
            batch = unique_ids[offset:offset + SQLITE_PARAMETER_BATCH]
            placeholders = ",".join("?" for _ in batch)
            rows = self.conn.execute(
                "SELECT student_id, uuid_filename, original_filename, file_path "
                f"FROM student_photos WHERE student_id IN ({placeholders})",
                batch,
            )
            photos.update((row["student_id"], StudentPhoto(**row)) for row in rows)
        return photos

    def get_all(self) -> list[StudentPhoto]:
        """Retorna totes les fotos registrades."""
        rows = self.conn.execute(
            "SELECT student_id, uuid_filename, original_filename, file_path "
            "FROM student_photos"
        ).fetchall()
        return [StudentPhoto(**row) for row in rows]

    def set(self, data: StudentPhoto) -> StudentPhoto:
        """Crea o substitueix la foto d'un alumne."""
        self.conn.execute(
            "INSERT INTO student_photos "
            "(student_id, uuid_filename, original_filename, file_path) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(student_id) DO UPDATE SET "
            "uuid_filename=excluded.uuid_filename, "
            "original_filename=excluded.original_filename, "
            "file_path=excluded.file_path",
            (data.student_id, data.uuid_filename, data.original_filename, data.file_path),
        )
        self.conn.commit()
        return data

    def delete(self, student_id: int) -> None:
        """Elimina el registre de la foto d'un alumne."""
        self.conn.execute("DELETE FROM student_photos WHERE student_id = ?", (student_id,))
        self.conn.commit()
