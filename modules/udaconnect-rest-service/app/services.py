import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.schemas import ConnectionSchema, LocationSchema, PersonSchema

import grpc
from proto import location_pb2
from proto import location_pb2_grpc
from proto import person_pb2
from proto import person_pb2_grpc

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

location_channel = grpc.insecure_channel("localhost:5005")
location_stub = location_pb2_grpc.LocationServiceStub(location_channel)
person_channel = grpc.insecure_channel("localhost:5005")
person_stub = person_pb2_grpc.PersonServiceStub(person_channel)

class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[ConnectionSchema]:
        location_message = location_pb2.LocationGetFilteredByDateMessage(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date
        )     
        locations_within_date_range: List = location_stub.GetFilteredByDate(location_message)

        # Cache all users in memory for quick lookup
        def person_message_mapper(person_message):
            person = PersonSchema()
            person.person_id = person_message.person_id
            person.first_name = person_message.first_name
            person.last_name = person_message.last_name
            person.comany_name = person_message.company_name

            return person
        
        person_map: Dict[str, PersonSchema] = {person_message.person_id: map(person_message_mapper, person_message) for person_message in person_stub.GetPersons().persons}

        # Prepare arguments for queries
        data = []
        for location in locations_within_date_range:
            data.append(
                {
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        result: List[ConnectionSchema] = []
        for line in tuple(data):
            location_message = location_pb2.LocationGetFilteredByRangeMessage(
                person_id=line.get("person_id"),
                longitude=line.get("longitude"),
                latitude=line.get("latitude"),
                meters=line.get("meters"),
                start_date=line.get("start_date"),
                end_date=line.get("end_date")
            )
            
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in location_stub.GetLocationsWithin(location_message).locations:
                location = LocationSchema(
                    id=location_id,
                    person_id=exposed_person_id,
                    longitude=exposed_long,
                    latitude=exposed_lat,
                    creation_time=exposed_time,
                )

                result.append(
                    ConnectionSchema(
                        person=person_map[exposed_person_id], location=location,
                    )
                )

        return result


class LocationService:
    @staticmethod
    def retrieve(location_id) -> LocationSchema:
        location_message = location_pb2.LocationGetMessage(
            location_id=location_id
        )        
        response = location_stub.Get(location_message)
        location = LocationSchema()
        location.id = response.location_id
        location.person_id = response.person_id
        location.longitude = response.longitude
        location.latitude = response.latitude
        location.creation_time = response.creation_time

        return location

    @staticmethod
    def create(location: Dict) -> LocationSchema:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        location_message = location_pb2.LocationMessage(
            location_id=location.get("id"),
            person_id=location.get("person_id"),
            longitude=location.get("longitude"),
            latitude=location.get("latitude"),
            creation_time=location.get("creation_time")
        )
        response = location_stub.Create(location_message)            
        new_location = LocationSchema()
        new_location.id = response.location_id
        new_location.person_id = response.person_id
        new_location.longitude = response.longitude
        new_location.latitude = response.latitude
        new_location.creation_time = response.creation_time

        return new_location


class PersonService:
    @staticmethod
    def create(person: Dict) -> PersonSchema:
        person_message = person_pb2.PersonMessage(
            person_id=person.get("id"),
            first_name=person.get("first_name"),
            last_name=person.get("last_name"),
            company_name=person.get("company_name")
        )
        response = person_stub.Create(person_message)
        new_person = PersonSchema()
        new_person.id = response.person_id
        new_person.first_name = response.first_name
        new_person.last_name = response.last_name
        new_person.company_name = response.company_name

        return new_person

    @staticmethod
    def retrieve(person_id: int) -> PersonSchema:
        person_message = person_pb2.PersonGetMessage(
            person_id=int(person_id),
        )
        response = person_stub.GetPerson(person_message)
        person = PersonSchema()
        person.id = response.person_id
        person.first_name = response.first_name
        person.last_name = response.last_name
        person.company_name = response.company_name

        return person

    @staticmethod
    def retrieve_all() -> List[PersonSchema]:
        response = person_stub.GetPersons(person_pb2.Empty())
        persons = []
        for person_message in response.persons:
            person = PersonSchema()
            person.id = person_message.person_id
            person.first_name = person_message.first_name
            person.last_name = person_message.last_name
            person.company_name = person_message.company_name
            persons.append(person)

        return persons