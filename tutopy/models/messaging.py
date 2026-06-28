from dataclasses import dataclass, fields
import datetime


@dataclass
class Category:
    """Categoria per classificar les notes de seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de la categoria (ex: "Conducta", "Acadèmic").
    """
    id: int
    name: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')


@dataclass
class CategoryNew:
    """Categoria per classificar les notes de seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de la categoria (ex: "Conducta", "Acadèmic").
    """
    name: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')

@dataclass
class AcademicCourse:
    """Curs acadèmic, generat de manera automàtica a partir dels registres
    
    Attributes:
        id: identificador a la base de dades.
        course: curs acadèmic, en format YYYY-YYYYY
    """
    id: int
    course: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')

@dataclass
class AcademicCourseNew:
    """Curs acadèmic, generat de manera automàtica a partir dels registres
    
    Attributes:
        course: curs acadèmic, en format YYYY-YYYYY
    """
    course: str

    def __post_init__(self):
        if not isinstance(self.course, str):
            raise ValueError(f'Expected course to be string got {type(self.course)}')


@dataclass
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
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')

    @property
    def full_name(self) -> str:
        """Retorna el nom complet: ``name`` + ``surnames``."""
        return f"{self.name}"+" "+f"{self.surnames}".strip()


@dataclass
class StudentNew:
    """Alumne del qual es fa el seguiment.

    Attributes:
        id: Identificador únic.
        name: Nom de l'alumne.
        surnames: Cognom o cognoms de l'alumne.
        group_name: Curs o grup al qual pertany (ex: "2n ESO A").
    """
    name: str
    surnames: str
    group_name: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')


@dataclass
class Note:
    """Nota de seguiment associada a un alumne i una categoria.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
        date: Data en format ISO ``YYYY-MM-DD``.
        content: Contingut textual de la nota.
    """
    id: int
    student_id: int
    category_id: int
    date: str
    course: int
    content: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")


@dataclass
class NoteNew:
    """Nota de seguiment associada a un alumne i una categoria.

    Attributes:
        student_id: Referència a l'alumne.
        category_id: Referència a la categoria.
        date: Data en format ISO ``YYYY-MM-DD``.
        content: Contingut textual de la nota.
    """
    student_id: int
    category_id: int
    date: str
    course: int
    content: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")


@dataclass
class NoteRecord:
    """Nota amb dades desnormalitzades per a visualització en taula.

    Atributs obtinguts amb un JOIN de les taules ``notes``,
    ``students`` i ``categories``.
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
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')
        try:
            datetime.date.fromisoformat(self.date)
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")


@dataclass
class Contact:
    """Persones de contacte associats a l'aulmne. Familiars o altres
    professionals externs al centre.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        name: Nom de la persona
        description: Descripció, per a descriure la relació amb l'alumne.
        phone: Numero de telèfon de la persona de contacte.
        email: Correu electrònic de la persona de contacte.
    """
    id: int
    student_id: int
    name: str
    description: str
    phone: str = ""
    email: str = ""

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')

@dataclass
class ContactNew:
    """Persones de contacte associats a l'aulmne. Familiars o altres
    professionals externs al centre.

    Attributes:
        student_id: Referència a l'alumne.
        name: Nom de la persona
        description: Descripció, per a descriure la relació amb l'alumne.
        phone: Numero de telèfon de la persona de contacte.
        email: Correu electrònic de la persona de contacte.
    """
    student_id: int
    name: str
    description: str
    phone: str = ""
    email: str = ""

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')



@dataclass
class StudentAnnotation:
    """Característiques o descriptores de l'alumne.

    Attributes:
        id: Identificador únic.
        student_id: Referència a l'alumne.
        content: Descripció.
    """
    id: int
    student_id: int
    content: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')


@dataclass
class StudentAnnotationNew:
    """Característiques o descriptores de l'alumne.

    Attributes:
        student_id: Referència a l'alumne.
        content: Descripció.
    """
    student_id: int
    content: str

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                 f'got {repr(value)}')
