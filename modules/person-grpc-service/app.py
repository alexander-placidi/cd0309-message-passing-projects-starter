import time, os
from concurrent import futures
from typing import List

import grpc
import person_pb2
import person_pb2_grpc

from services import PersonService
from models import Person
from config import config_by_name


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
        persons_message = person_pb2.PersonMessageList
        for person in persons:
            person_message = person_pb2.PersonMessage(
                person_id=person.id,
                first_name=person.first_name,
                last_name=person.last_name,
                company_name=person.company_name
            )
            persons_message.persons.extend(person_message)

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
            person_id=person.person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            company_name=person.company_name
        )


server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServicer(), server)

grpc_port = config_by_name(os.getenv("FLASK_ENV") or "test")
print(f"Server starting on port {grpc_port}...")
server.add_insecure_port(f"[::]:{grpc_port}")
server.start()
# Keep thread alive
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    server.stop(0)