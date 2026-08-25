"""Persistència de categories de seguiment."""

from typing import Optional

from tutopy.models.messaging import Category, CategoryNew


class CategoryDAO:
    """Llegeix i modifica categories mitjançant una connexió gestionada."""

    def __init__(self, conn):
        """Inicialitza el DAO amb la connexió compartida."""
        self.conn = conn

    def _get_notes_count(self, category_id: int) -> int:
        """Retorna el nombre de notes associades a una categoria."""
        return self.conn.execute(
            "SELECT COUNT(*) FROM notes WHERE category_id = ?", (category_id,)
        ).fetchone()[0]

    def get_all(self) -> list[Category]:
        """Retorna totes les categories, ordenades per nom."""
        rows = self.conn.execute(
            "SELECT id, name FROM categories ORDER BY name"
        ).fetchall()
        return [Category(**row) for row in rows]

    def get_by_name(self, name: str) -> Optional[Category]:
        """Retorna la categoria amb aquest nom, o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, name FROM categories WHERE name = ?", (name,)
        ).fetchone()
        return Category(**row) if row else None

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retorna una categoria o ``None`` si no existeix."""
        row = self.conn.execute(
            "SELECT id, name FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        return Category(**row) if row else None

    def create(self, data: CategoryNew) -> Category:
        """Crea una nova categoria."""
        cur = self.conn.execute(
            "INSERT INTO categories (name) VALUES (?)", (data.name,)
        )
        self.conn.commit()
        return Category(id=cur.lastrowid, name=data.name)

    def rename(self, data: Category):
        """Canvia el nom d'una categoria existent."""
        category_id = data.id
        new_name = data.name
        self.conn.execute(
            "UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id)
        )
        self.conn.commit()

    def is_deletable(self, category_id: int) -> bool:
        """Indica si la categoria no té cap nota associada."""
        return self._get_notes_count(category_id) == 0

    def delete(self, category_id: int):
        """Elimina una categoria sense notes associades.

        Raises:
            ValueError: Si encara hi ha notes que usen la categoria.
        """
        count = self._get_notes_count(category_id)
        if count > 0:
            raise ValueError(
                f"No es pot eliminar: {count} notes usen aquesta categoria"
            )
        self.conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
