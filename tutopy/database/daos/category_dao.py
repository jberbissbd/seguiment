from typing import Optional
from tutopy.models.messaging import Category, CategoryNew


class CategoryDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self) -> list[Category]:
        rows = self.conn.execute(
            "SELECT * FROM categories ORDER BY name"
        ).fetchall()
        return [Category(**row) for row in rows]

    def get_by_name(self, name: str) -> Optional[Category]:
        row = self.conn.execute(
            "SELECT * FROM categories WHERE name = ?", (name,)
        ).fetchone()
        return Category(**row) if row else None

    def create(self, data: CategoryNew) -> Category:
        cur = self.conn.execute(
            "INSERT INTO categories (name) VALUES (?)", (data.name,)
        )
        self.conn.commit()
        return Category(id=cur.lastrowid, name=data.name)

    def rename(self, id: int, new_name: str):
        self.conn.execute(
            "UPDATE categories SET name = ? WHERE id = ?", (new_name, id)
        )
        self.conn.commit()

    def delete(self, id: int):
        count = self.conn.execute(
            "SELECT COUNT(*) FROM notes WHERE category_id = ?", (id,)
        ).fetchone()[0]
        if count > 0:
            raise ValueError(
                f"No es pot eliminar: {count} notes usen aquesta categoria"
            )
        self.conn.execute("DELETE FROM categories WHERE id = ?", (id,))
        self.conn.commit()
