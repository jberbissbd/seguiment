"""Models de domini: alumnes, notes, contactes, documents i entitats relacionades."""

from dataclasses import dataclass, fields
from typing import Optional, Union, get_args, get_origin
import datetime

INVALID_DATE_MESSAGE = "Incorrect data format, should be YYYY-MM-DD"


def _matches_type(value, expected_type) -> bool:
    """Comprova tipus simples i unions com ``Optional[T]``."""
    origin = get_origin(expected_type)
    if origin is Union:
        return any(_matches_type(value, option) for option in get_args(expected_type))
    if expected_type is int and isinstance(value, bool):
        return False
    return isinstance(value, expected_type)


def _validate(dataclass_obj):
    for field in fields(dataclass_obj):
        value = getattr(dataclass_obj, field.name)
        if not _matches_type(value, field.type):
            raise ValueError(
                f"Expected {field.name} to be {field.type}, "
                f"got {repr(value)}"
            )


@dataclass(frozen=True, slots=True)
class Category:
    """Categoria per classificar les notes de seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de la categoria (ex: "Conducta", "Acadèmic").
    """
    id: int
    name: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)


@dataclass(frozen=True, slots=True)
class CategoryNew:
    """Categoria per classificar les notes de seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de la categoria (ex: "Conducta", "Acadèmic").
    """
    name: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

@dataclass(frozen=True, slots=True)
class AcademicCourse:
    """Curs acadèmic, generat de manera automàtica a partir dels registres.

    Attributes:
        id: Identificador a la base de dades.
        course: Curs acadèmic, en format YYYY-YYYY.
    """
    id: int
    course: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

@dataclass(frozen=True, slots=True)
class AcademicCourseNew:
    """Curs acadèmic, generat de manera automàtica a partir dels registres.

    Attributes:
        course: Curs acadèmic, en format YYYY-YYYY.
    """
    course: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)


@dataclass(frozen=True, slots=True)
class Student:
    """Alumne del qual es fa el seguiment.

    Attributes:
        id: Identificador únic.
        uuid: uuid(4) de l'alumne, generat al vol.
        name: Nom de l'alumne.
        surnames: Cognom o cognoms de l'alumne.
        group_name: Curs o grup al qual pertany (ex: "2n ESO A").
    """
    id: int
    uuid: str
    name: str
    surnames: str
    group_name: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

    @property
    def full_name(self) -> str:
        """Retorna el nom complet: ``name`` + ``surnames``."""
        return f"{self.name} {self.surnames}".strip()

    @property
    def filing_name(self) -> str:
        """Retorna el nom en format administratiu ``cognoms, nom``."""
        return f"{self.surnames}, {self.name}" if self.surnames else self.name


@dataclass(frozen=True, slots=True)
class StudentNew:
    """Alumne del qual es fa el seguiment.

    Attributes:
        name: Nom de l'alumne.
        surnames: Cognom o cognoms de l'alumne.
        group_name: Curs o grup al qual pertany (ex: "2n ESO A").
    """
    name: str
    surnames: str
    group_name: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)


@dataclass(frozen=True, slots=True)
class Note:
    """Registre de seguiment datat, classificat i associat a un alumne.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
        date: Data en format ISO ``YYYY-MM-DD``.
        course_id: Referència al curs acadèmic.
        content: Contingut textual de la nota.
    """
    id: int
    student_id: int
    category_id: int
    date: str
    course_id: int
    content: str

    def __post_init__(self):
        """Valida els tipus dels camps i el format ISO de la data."""
        _validate(self)
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError as error:
            raise ValueError(INVALID_DATE_MESSAGE) from error


@dataclass(frozen=True, slots=True)
class NoteNew:
    """Dades d'entrada per crear un registre de seguiment datat.

    Attributes:
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
        date: Data en format ISO ``YYYY-MM-DD``.
        course_id: Referència al curs acadèmic.
        content: Contingut textual de la nota.
    """
    student_id: int
    category_id: int
    date: str
    course_id: int
    content: str

    def __post_init__(self):
        """Valida els tipus dels camps i el format ISO de la data."""
        _validate(self)
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError as error:
            raise ValueError(INVALID_DATE_MESSAGE) from error


@dataclass(frozen=True, slots=True)
class NoteRecord:
    """Nota amb dades desnormalitzades per a visualització en taula.

    Obtinguda amb un JOIN de les taules ``notes``, ``students`` i
    ``categories``.

    Attributes:
        note_id: Identificador de la nota.
        date: Data en format ISO ``YYYY-MM-DD``.
        student_name: Nom complet de l'alumne (``name`` + ``surnames``).
        group_name: Grup de l'alumne.
        category_name: Nom de la categoria.
        content: Contingut textual de la nota.
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
    """
    note_id: int
    date: str
    student_name: str
    group_name: str
    category_name: str
    content: str
    student_id: int
    category_id: int

    def __post_init__(self):
        """Valida els tipus dels camps i el format ISO de la data."""
        _validate(self)
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError as error:
            raise ValueError(INVALID_DATE_MESSAGE) from error


@dataclass(frozen=True, slots=True)
class Contact:
    """Persona de contacte associada a l'alumne: familiar o professional extern.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        name: Nom de la persona.
        description: Descripció, per a descriure la relació amb l'alumne.
        phone: Número de telèfon de la persona de contacte.
        email: Correu electrònic de la persona de contacte.
    """
    id: int
    student_id: int
    name: str
    description: str
    phone: str = ""
    email: str = ""

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

@dataclass(frozen=True, slots=True)
class ContactNew:
    """Persona de contacte associada a l'alumne: familiar o professional extern.

    Attributes:
        student_id: Referència a l'alumne.
        name: Nom de la persona.
        description: Descripció, per a descriure la relació amb l'alumne.
        phone: Número de telèfon de la persona de contacte.
        email: Correu electrònic de la persona de contacte.
    """
    student_id: int
    name: str
    description: str
    phone: str = ""
    email: str = ""

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)



@dataclass(frozen=True, slots=True)
class StudentAnnotation:
    """Descriptor general i no datat d'un alumne.

    No és una nota de seguiment: no té data, categoria ni curs acadèmic.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        content: Descripció.
    """
    id: int
    student_id: int
    content: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

@dataclass(frozen=True, slots=True)
class StudentAnnotationNew:
    """Dades d'entrada per crear un descriptor general i no datat de l'alumne.

    Attributes:
        student_id: Referència a l'alumne.
        content: Descripció.
    """
    student_id: int
    content: str

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)

@dataclass(frozen=True, slots=True)
class StudentDocument:
    """Document adjuntat a l'expedient d'un alumne.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        name: Nom visible del document.
        description: Descripció del document.
        uuid_filename: Nom del fitxer al disc (UUID, evita col·lisions).
        original_filename: Nom original del fitxer tal com es va pujar.
        file_path: Ruta relativa on es guarda el fitxer.
        date: Data associada al document, en format ``YYYY-MM-DD``.
        course_id: Referència al curs acadèmic (opcional).
    """
    id: int
    student_id: int
    name: str
    description: str
    uuid_filename: str
    original_filename: str
    file_path: str = ""
    date: str = ""
    course_id: Optional[int] = None

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)


@dataclass(frozen=True, slots=True)
class StudentDocumentNew:
    """Dades d'entrada per registrar un nou document per a un alumne.

    Attributes:
        student_id: Referència a l'alumne.
        name: Nom visible del document.
        description: Descripció del document.
        uuid_filename: Nom del fitxer al disc (UUID, evita col·lisions).
        original_filename: Nom original del fitxer tal com es va pujar.
        file_path: Ruta relativa on es guarda el fitxer.
        date: Data associada al document, en format ``YYYY-MM-DD``.
        course_id: Referència al curs acadèmic (opcional).
    """
    student_id: int
    name: str
    description: str
    uuid_filename: str
    original_filename: str
    file_path: str = ""
    date: str = ""
    course_id: Optional[int] = None

    def __post_init__(self):
        """Valida els tipus dels camps just després de la inicialització."""
        _validate(self)


@dataclass(frozen=True, slots=True)
class StudentGroupHistory:
    """Històric de grups d'un alumne.
    
    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        group_name: Nom del grup (ex: "4t A").
        start_date: Data d'inici en format YYYY-MM-DD.
        end_date: Data de final en format YYYY-MM-DD (NULL si és el grup actual).
        academic_course_id: Referència al curs acadèmic (opcional).
    """
    id: int
    student_id: int
    group_name: str
    start_date: str
    end_date: Optional[str] = None
    academic_course_id: Optional[int] = None

    def __post_init__(self):
        """Valida els tipus dels camps i el format ISO de ``start_date``/``end_date``."""
        _validate(self)
        try:
            datetime.date.fromisoformat(self.start_date)
        except ValueError as error:
            raise ValueError("Incorrect start_date format, should be YYYY-MM-DD") from error
        if self.end_date:
            try:
                datetime.date.fromisoformat(self.end_date)
            except ValueError as error:
                raise ValueError("Incorrect end_date format, should be YYYY-MM-DD or None") from error


@dataclass(frozen=True, slots=True)
class StudentGroupHistoryNew:
    """Nou registre d'històric de grup d'un alumne.
    
    Attributes:
        student_id: Referència a l'alumne.
        group_name: Nom del grup (ex: "4t A").
        start_date: Data d'inici en format YYYY-MM-DD.
        end_date: Data de final en format YYYY-MM-DD (NULL si és el grup actual).
        academic_course_id: Referència al curs acadèmic (opcional).
    """
    student_id: int
    group_name: str
    start_date: str
    end_date: Optional[str] = None
    academic_course_id: Optional[int] = None

    def __post_init__(self):
        """Valida els tipus dels camps i el format ISO de ``start_date``/``end_date``."""
        _validate(self)
        try:
            datetime.date.fromisoformat(self.start_date)
        except ValueError as error:
            raise ValueError("Incorrect start_date format, should be YYYY-MM-DD") from error
        if self.end_date:
            try:
                datetime.date.fromisoformat(self.end_date)
            except ValueError as error:
                raise ValueError("Incorrect end_date format, should be YYYY-MM-DD or None") from error


@dataclass(frozen=True, slots=True)
class StudentDetails:
    """Alumne amb les relacions necessàries per a la vista de detall."""

    student: Student
    contacts: tuple[Contact, ...]
    documents: tuple[StudentDocument, ...]

    def __getattr__(self, name):
        """Delega els atributs no trobats a ``self.student`` (ex: ``full_name``)."""
        return getattr(self.student, name)
