"""Omple una base de dades de desenvolupament amb dades fictícies completes.

Pensat per provar l'aplicació (en particular, la gestió de fotos d'alumnes)
sense cap risc d'alterar la instal·lació real que ja es fa servir en aquesta
màquina. Exigeix que `TUTOPY_DATA_DIR` estigui definida, de manera que sigui
físicament impossible sembrar per error la base de dades real
(`~/.local/share/Tutopy` o equivalent): sense aquesta variable, `main()` no
fa res.

Ús:
    TUTOPY_DATA_DIR=/ruta/dev-data python scripts/seed_dev_data.py

Un cop sembrada, l'aplicació es pot executar sobre les mateixes dades amb:
    TUTOPY_DATA_DIR=/ruta/dev-data python -m tutopy.main
"""

import os
import random
import sys

from tutopy.application import create_services
from tutopy.database.database import Database
from tutopy.models.messaging import CategoryNew, ContactNew, NoteNew, StudentNew
from tutopy.services.directories import get_db_path

RANDOM_SEED = 20261027

FIRST_NAMES = (
    "Laia", "Marc", "Anna", "Jordi", "Núria", "Pau", "Clara", "Oriol",
    "Judit", "Arnau", "Maria", "Pol", "Berta", "Biel", "Carla", "Gerard",
    "Emma", "Eric", "Alba", "Roc", "Mireia", "Dídac", "Ona", "Max",
)
SURNAMES = (
    "Soler", "Puig", "Serra", "Vidal", "Roca", "Font", "Reixach", "Vila",
    "Camps", "Riera", "Bosch", "Prats", "Oliver", "Costa", "Sala", "Ferrer",
)
GROUPS = ("1r ESO A", "1r ESO B", "2n ESO A", "3r ESO B", "4t ESO A")
CATEGORIES = ("Conducta", "Acadèmic", "Convivència")
ACADEMIC_COURSE = "2025-2026"
NOTE_DATES = ("2025-10-06", "2025-11-14", "2026-01-20", "2026-02-18")
NOTE_CONTENTS = (
    "Participa activament a classe.",
    "Ha lliurat la feina fora de termini.",
    "Mostra una bona actitud amb els companys.",
    "Cal fer seguiment de l'assistència.",
    "Millora notable respecte al trimestre anterior.",
)
STUDENTS_PER_GROUP = 8


def seed(services) -> None:
    """Crea alumnes, grups, categories, notes i contactes fictícies via els serveis."""
    categories = [services.categories.create(CategoryNew(name)) for name in CATEGORIES]
    course = services.academic_courses.get_or_create(ACADEMIC_COURSE)
    for group_name in GROUPS:
        for _ in range(STUDENTS_PER_GROUP):
            student = services.students.create(
                StudentNew(
                    random.choice(FIRST_NAMES), random.choice(SURNAMES), group_name,
                ),
                academic_course_id=course.id,
            )
            if random.random() < 0.6:
                category = random.choice(categories)
                services.notes.create(NoteNew(
                    student.id, category.id, random.choice(NOTE_DATES), course.id,
                    random.choice(NOTE_CONTENTS),
                ))
            if random.random() < 0.3:
                services.contacts.create(ContactNew(
                    student.id, "Família", "Contacte familiar de referència",
                    "600000000", "familia@example.com",
                ))


def main() -> int:
    """Sembra dades fictícies a `TUTOPY_DATA_DIR`, o atura's si no està definida."""
    if not os.environ.get("TUTOPY_DATA_DIR"):
        print(
            "Cal definir TUTOPY_DATA_DIR abans d'executar aquest script, "
            "per evitar sembrar per error la base de dades real.",
            file=sys.stderr,
        )
        return 1
    random.seed(RANDOM_SEED)
    database = Database(str(get_db_path())).connect()
    try:
        seed(create_services(database))
    finally:
        database.close()
    print(f"Dades fictícies creades a {os.environ['TUTOPY_DATA_DIR']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
