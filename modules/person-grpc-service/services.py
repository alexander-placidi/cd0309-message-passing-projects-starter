import logging, os, copy
from typing import Dict, List

from config import config_by_name
from models import Person
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

env = os.getenv("GRPC_ENV") or "test"
engine = create_engine(config_by_name[env].SQLALCHEMY_DATABASE_URI)

class PersonService:
    @staticmethod
    def create(person: Dict) -> Person:
        new_person = Person()
        new_person.id = person["id"]
        new_person.first_name = person["first_name"]
        new_person.last_name = person["last_name"]
        new_person.company_name = person["company_name"]

        with Session(engine, expire_on_commit=False) as session:
            session.add(new_person)
            session.commit()

        return new_person

    @staticmethod
    def retrieve(person_id: int) -> Person:
        with Session(engine, expire_on_commit=False) as session:
            person = session.execute(select(Person).where(Person.id == person_id)).scalar_one()

        return person

    @staticmethod
    def retrieve_all() -> List[Person]:
        with Session(engine, expire_on_commit=False) as session:
            persons = session.execute(select(Person)).scalars().all()

        return persons
    