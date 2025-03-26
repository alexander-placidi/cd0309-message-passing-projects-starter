from typing import List

from app.services import PersonService
from proto import person_pb2, person_pb2_grpc
from app.models import Person


class PersonServicer(person_pb2_grpc.PersonServiceServicer):
    def GetPerson(self, request, context):
        person_id = request.person_id
        person: Person = PersonService.retrieve(person_id=person_id)
        person_message = person_pb2.PersonMessage(
            person_id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            company_name=person.company_name
        )
        return person_message      

    def GetPersons(self, request, context):
        persons: List[Person] = PersonService.retrieve_all()
        persons_message = person_pb2.PersonMessageList()
        for person in persons:
            person_message = person_pb2.PersonMessage(
                person_id=person.id,
                first_name=person.first_name,
                last_name=person.last_name,
                company_name=person.company_name
            )
            persons_message.persons.append(person_message)

        return persons_message


    def Create(self, request, context):
        person_request = {
            "id": request.person_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "company_name": request.company_name
        }
        person: Person = PersonService.create(person_request)

        return person_pb2.PersonMessage(
            person_id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            company_name=person.company_name
        )