import logging, os, json, grpc
from datetime import datetime, timedelta
from typing import Dict, List
from kafka import KafkaProducer
from kafka.errors import KafkaError
from app.errors import log_grpc_error

from app.dataclasses import Person, Location, Connection
from app.utils import str_to_datetime, datetime_to_str, location_protobuf_to_class, person_protobuf_to_class
from app.config import config_by_name

from proto import location_pb2
from proto import location_pb2_grpc
from proto import person_pb2
from proto import person_pb2_grpc


config = config_by_name[os.getenv("FLASK_ENV") or "test"]

location_channel = grpc.insecure_channel(f"{config.GRPC_LOCATION_SERVICE_HOST}:{config.GRPC_LOCATION_SERVICE_PORT}")
location_stub = location_pb2_grpc.LocationServiceStub(location_channel)

person_channel = grpc.insecure_channel(f"{config.GRPC_PERSON_SERVICE_HOST}:{config.GRPC_PERSON_SERVICE_PORT}")
person_stub = person_pb2_grpc.PersonServiceStub(person_channel)

kafka_topic = config.KAFKA_TOPIC
kafka_bootstrap_servers = config.KAFKA_BOOTSTRAP_SERVERS

producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers, 
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda m: json.dumps(m).encode('utf-8')
)

class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        location_message = location_pb2.LocationGetContactsMessage(
            person_id=person_id,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            meters=meters
        )
        
        locations: List[location_pb2.LocationMessage]
        try:
            locations = location_stub.GetContacts(location_message).locations
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)

        adjacent_locations: List[Location] = [location_protobuf_to_class(loc) for loc in locations]

        # Cache all users in memory for quick lookup                
        persons: List[person_pb2.PersonMessage]
        try:
            persons = person_stub.GetPersons(person_pb2.Empty()).persons
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)
        
        person_map: Dict[str, Person] = {person.id: person for person in map(person_protobuf_to_class, persons)}
        
        result: List[Connection] = []
            
        for location in adjacent_locations:
            result.append(Connection(
                person=person_map[location.person_id],
                location=location
            ))

        return result


class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location_message = location_pb2.LocationGetMessage(
            location_id=int(location_id)
        )

        response: location_pb2.LocationMessage
        try:
            response = location_stub.Get(location_message)
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)         

        return Location(
            id=response.location_id,
            person_id=response.person_id,
            longitude=response.longitude,
            latitude=response.latitude,
            creation_time=str_to_datetime(response.creation_time)
        )

    @staticmethod
    def create(location: Location) -> Location:
        try:
            producer.send(kafka_topic, key=str(location.id), value={
                "id": location.id,
                "person_id": location.person_id,
                "longitude": location.longitude,
                "latitude": location.latitude,
                "creation_time": datetime_to_str(location.creation_time)
            })
            producer.flush()
        except KafkaError as kafka_error:
            logging.error(f"kafka producer error: {kafka_error}")
            raise Exception(kafka_error)

        return location


class PersonService:
    @staticmethod
    def create(person: Person) -> Person:
        person_message = person_pb2.PersonMessage(
            person_id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            company_name=person.company_name
        )
        
        response: person_pb2.PersonMessage
        try: 
            response = person_stub.Create(person_message)
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)     

        return Person(
            id=response.person_id,
            first_name=response.first_name,
            last_name=response.last_name,
            company_name=response.company_name
        )

    @staticmethod
    def retrieve(person_id: int) -> Person:
        person_message = person_pb2.PersonGetMessage(
            person_id=int(person_id),
        )
        
        response: person_pb2.PersonMessage
        try:
            response = person_stub.GetPerson(person_message)
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)  
        
        return Person(
            id=response.person_id,
            first_name=response.first_name,
            last_name=response.last_name,
            company_name=response.company_name
        )

    @staticmethod
    def retrieve_all() -> List[Person]:
        response: List[person_pb2.PersonMessage] 
        try:
            response = person_stub.GetPersons(person_pb2.Empty())
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)
            raise Exception(rpc_error)
         
        persons = []
        for person_message in response.persons:
            persons.append(Person(
                id=person_message.person_id,
                first_name=person_message.first_name,
                last_name=person_message.last_name,
                company_name=person_message.company_name                
            ))

        return persons