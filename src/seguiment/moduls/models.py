from dataclasses import dataclass
from datetime import datetime

@dataclass
class Student:
    id: str
    group: str
    full_name: str

@dataclass
class TrackingEntry:
    student_id: str
    date: datetime
    category: str
    description: str
    trimestre: str