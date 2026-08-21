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


class FileCleanupError(DomainError):
    """L'operació s'ha completat, però ha quedat un fitxer per netejar."""


class TransferAuthenticationError(DomainError, ValueError):
    """La contrasenya no desxifra el paquet o aquest ha estat manipulat."""


class TransferFormatError(DomainError, ValueError):
    """El fitxer no compleix el format de transferència esperat."""
