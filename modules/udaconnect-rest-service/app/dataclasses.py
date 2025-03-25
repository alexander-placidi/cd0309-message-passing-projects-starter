from dataclasses import dataclass
from datetime import datetime

@dataclass
class Person:
    """Person Dataclass"""
    id: int
    first_name: str
    last_name: str
    company_name: str

@dataclass
class Location:
    """Location Dataclass"""
    id: int
    person_id: int
    longitude: str
    latitude: str
    creation_time: datetime

@dataclass
class Connection:
    """Connection Dataclass"""
    location: Location
    person: Person