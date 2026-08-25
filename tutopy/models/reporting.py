"""Models per a la configuració i generació d'informes XLSX."""

from dataclasses import dataclass

from tutopy.models.messaging import (
    Category,
    Note,
    Student,
    StudentGroupHistory,
)


@dataclass(frozen=True)
class TermConfiguration:
    """Dates d'inici dels trimestres per a un curs acadèmic i grup.

    Attributes:
        id: Identificador únic.
        academic_course_id: Referència al curs acadèmic.
        group_name: Grup al qual s'aplica la configuració.
        second_term_start: Data d'inici del segon trimestre (``YYYY-MM-DD``).
        third_term_start: Data d'inici del tercer trimestre (``YYYY-MM-DD``).
    """

    id: int
    academic_course_id: int
    group_name: str
    second_term_start: str
    third_term_start: str


@dataclass(frozen=True)
class TermConfigurationNew:
    """Dades d'entrada per crear o actualitzar una configuració de trimestres.

    Attributes:
        academic_course_id: Referència al curs acadèmic.
        group_name: Grup al qual s'aplica la configuració.
        second_term_start: Data d'inici del segon trimestre (``YYYY-MM-DD``).
        third_term_start: Data d'inici del tercer trimestre (``YYYY-MM-DD``).
    """

    academic_course_id: int
    group_name: str
    second_term_start: str
    third_term_start: str


@dataclass(frozen=True)
class BatchExportFailure:
    """Fallada en generar l'informe d'un alumne concret dins d'una exportació per lots.

    Attributes:
        student_id: Alumne pel qual ha fallat la generació.
        student_name: Nom complet de l'alumne, per mostrar-lo a l'usuari.
        reason: Descripció llegible de l'error.
    """

    student_id: int
    student_name: str
    reason: str


@dataclass(frozen=True)
class BatchExportResult:
    """Resultat d'exportar informes per a diversos alumnes.

    Attributes:
        destination: Carpeta o fitxer de destinació de l'exportació.
        exported: Nombre d'informes generats correctament.
        failures: Fallades individuals, si n'hi ha hagut.
        cancelled: Cert si l'usuari ha cancel·lat l'operació abans d'acabar.
    """

    destination: str
    exported: int
    failures: tuple[BatchExportFailure, ...] = ()
    cancelled: bool = False


@dataclass(frozen=True, slots=True)
class ReportBatchData:
    """Snapshot compartit per generar un o més informes sense consultes N+1.

    Attributes:
        students: Alumnes indexats pel seu identificador.
        notes: Notes de cada alumne, indexades pel seu identificador.
        course_names: Nom de cada curs acadèmic, indexat pel seu identificador.
        categories: Totes les categories disponibles.
        histories: Històric de grups de cada alumne, indexat pel seu identificador.
        term_configurations: Configuració de trimestres per parella
            ``(academic_course_id, group_name)``.
        header_image: Ruta de la imatge de capçalera dels informes, o ``None``.
    """

    students: dict[int, Student]
    notes: dict[int, list[Note]]
    course_names: dict[int, str]
    categories: tuple[Category, ...]
    histories: dict[int, list[StudentGroupHistory]]
    term_configurations: dict[tuple[int, str], TermConfiguration]
    header_image: str | None
