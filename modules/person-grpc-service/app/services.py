import logging
from typing import Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Person
from app.schemas import PersonSchema
from app.session import session


class PersonService:
    @staticmethod
    def create(person: Dict) -> Person:
        validation_results: Dict = PersonSchema().validate(person)
        if validation_results:
            logging.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")
        
        new_person = Person()
        new_person.id = person["id"]
        new_person.first_name = person["first_name"]
        new_person.last_name = person["last_name"]
        new_person.company_name = person["company_name"]

        session.add(new_person)
        session.commit()

        return new_person

    @staticmethod
    def retrieve(person_id: int) -> Person:
        person = session.execute(
            select(Person).where(Person.id == person_id)
        ).scalar_one()

        return person

    @staticmethod
    def retrieve_all() -> List[Person]:
        persons = session.execute(select(Person)).scalars().all()

        return persons
    