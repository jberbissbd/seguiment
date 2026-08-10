class DomainError(Exception):
    """Error de negoci que els controladors poden mostrar a l'usuari."""


class ValidationError(DomainError, ValueError):
    """Les dades rebudes no compleixen el contracte del domini."""


class EntityNotFoundError(DomainError, ValueError):
    """L'entitat requerida no existeix."""


class DuplicateEntityError(DomainError, ValueError):
    """L'operació crearia una entitat duplicada."""


class EntityInUseError(DomainError, ValueError):
    """L'entitat no es pot modificar o eliminar perquè està en ús."""
