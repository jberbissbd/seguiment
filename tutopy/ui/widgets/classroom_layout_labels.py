"""Etiquetes en català per als valors de configuració de la distribució d'aula.

Mòdul fulla (sense importar cap altre widget de `classroom_layout_*`)
perquè la vista, el diàleg de plantilla i el panell de preferències el
puguin importar tots tres sense crear cap dependència circular.
"""

from tutopy.models.classroom_layout_fill import LeftoverCriterion, OrderBy

TEACHER_MODE_LABELS = {"strip": "Franja", "grid": "Dins la graella"}
TEACHER_POSITION_LABELS = {"left": "Esquerra", "center": "Centre", "right": "Dreta"}
LEFTOVER_LABELS = {
    LeftoverCriterion.BACK: "Al fons",
    LeftoverCriterion.BACK_CENTERED: "Al fons, centrats",
    LeftoverCriterion.SPREAD_BY_BLOCKS: "Repartits per blocs",
    LeftoverCriterion.FRONT: "Al davant",
    LeftoverCriterion.REMOVE: "Eliminar",
}
FILL_ORDER_LABELS = {OrderBy.ROWS: "Per files", OrderBy.BLOCKS: "Per blocs"}
