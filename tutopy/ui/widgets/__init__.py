"""
Paquet de widgets de la UI.

Aquest paquet conté tots els widgets personalitzats de l'aplicació.
"""

from .sidebar import Sidebar
from .student_list import StudentListWidget
from .student_detail_panel import StudentDetailPanel
from .student_list_item import StudentListItem
from .annotation_filter import AnnotationFilterWidget

__all__ = [
    "Sidebar",
    "StudentListWidget",
    "StudentDetailPanel",
    "StudentListItem",
    "AnnotationFilterWidget",
]
