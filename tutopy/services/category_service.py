from typing import Optional
from tutopy.database.daos.category_dao import CategoryDAO
from tutopy.models.messaging import Category, CategoryNew
from tutopy.services.validation_service import ValidationService
from tutopy.services.exceptions import (
    DuplicateEntityError, EntityInUseError, EntityNotFoundError,
)


class CategoryService:
    """Servei per gestionar categories de notes.
    
    Proporciona una capa d'abstracció sobre CategoryDAO amb validacions
    i lògica de negoci addicional.
    """

    def __init__(self, category_dao: CategoryDAO, validation_service: ValidationService = None):
        self.category_dao = category_dao
        self.validation_service = validation_service or ValidationService(category_dao)

    def get_all(self) -> list[Category]:
        """Retorna totes les categories ordenades per nom."""
        return self.category_dao.get_all()

    def get_by_id(self, id: int) -> Optional[Category]:
        """Retorna una categoria pel seu ID, o None si no existeix."""
        return self.category_dao.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Category]:
        """Retorna una categoria pel seu nom, o None si no existeix."""
        return self.category_dao.get_by_name(name)

    def create(self, data: CategoryNew) -> Category:
        """Crea una nova categoria amb validació.
        
        Args:
            data: Dades de la nova categoria (nom).
            
        Returns:
            Category: La categoria creada.
            
        Raises:
            ValueError: Si ja existeix una categoria amb el mateix nom.
        """
        name = self.validation_service.required_text(
            data.name, "El nom de la categoria no pot estar buit."
        )
        if self.category_dao.get_by_name(name):
            raise DuplicateEntityError(f"Ja existeix una categoria amb el nom '{name}'")
        return self.category_dao.create(CategoryNew(name))

    def rename(self, category: Category) -> None:
        """Renomena una categoria existent amb validació.
        
        Args:
            category: Category amb el nou nom.
            
        Raises:
            ValueError: Si la categoria no existeix o té notes associades.
        """
        existing = self.category_dao.get_by_id(category.id)
        if not existing:
            raise EntityNotFoundError(f"No existeix la categoria amb ID {category.id}")
        name = self.validation_service.required_text(
            category.name, "El nom de la categoria no pot estar buit."
        )
        
        # Verificar que no hi hagi una altra categoria amb el mateix nom
        existing_with_name = self.category_dao.get_by_name(name)
        if existing_with_name and existing_with_name.id != category.id:
            raise DuplicateEntityError(
                f"Ja existeix una categoria amb el nom '{name}'"
            )
        self.category_dao.rename(Category(category.id, name))

    def can_delete(self, id: int) -> bool:
        """Comprova si una categoria es pot eliminar.
        
        Args:
            id: ID de la categoria.
            
        Returns:
            bool: True si es pot eliminar, False en cas contrari.
        """
        return self.validation_service.can_delete_category(id)

    def delete(self, id: int) -> None:
        """Elimina una categoria si no té notes associades.
        
        Args:
            id: ID de la categoria a eliminar.
            
        Raises:
            ValueError: Si la categoria té notes associades.
        """
        if self.category_dao.get_by_id(id) is None:
            raise EntityNotFoundError(f"No existeix la categoria amb ID {id}")
        if not self.validation_service.can_delete_category(id):
            raise EntityInUseError("No es pot eliminar: la categoria té notes associades")
        self.category_dao.delete(id)
