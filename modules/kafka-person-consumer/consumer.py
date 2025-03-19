from kafka import KafkaConsumer
from schemas import PersonSchema
from marshmallow import ValidationError
from marshmallow import EXCLUDE
import json
import grpc
import person_pb2
import person_pb2_grpc

@staticmethod
def subscribe(kafka_topic:str, kafka_bootstrap_servers: list[str], consumer_group_id: str) -> None:
    consumer = KafkaConsumer(
        kafka_topic, 
        bootstrap_servers=kafka_bootstrap_servers, 
        group_id=consumer_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    channel = grpc.insecure_channel("localhost:5005")
    stub = person_pb2_grpc.PersonServiceStub(channel)
    for message in consumer:
        schema = PersonSchema()
        try:
            person = schema.load(message.value, unknown=EXCLUDE)
            print(person)
            person_message = person_pb2.PersonMessage(
                person_id=person.get("person_id"),
                first_name=person.get("first_name"),
                last_name=person.get("last_name"),
                company_name=person.get("company_name")
            )
            response = stub.Create(person_message)

        except ValidationError as err:
            print(err.messages)