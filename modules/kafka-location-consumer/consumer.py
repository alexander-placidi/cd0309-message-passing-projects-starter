from kafka import KafkaConsumer
from schemas import LocationSchema
from marshmallow import ValidationError
from marshmallow import EXCLUDE
import json
import grpc
import location_pb2
import location_pb2_grpc

@staticmethod
def subscribe(kafka_topic:str, kafka_bootstrap_servers: list[str], consumer_group_id: str) -> None:
    consumer = KafkaConsumer(
        kafka_topic, 
        bootstrap_servers=kafka_bootstrap_servers, 
        group_id=consumer_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    channel = grpc.insecure_channel("localhost:5005")
    stub = location_pb2_grpc.LocationServiceStub(channel)
    for message in consumer:
        schema = LocationSchema()
        try:
            location = schema.load(message.value, unknown=EXCLUDE)
            print(location)
            location_message = location_pb2.LocationMessage(
                location_id=location.get("id"),
                person_id=location.get("person_id"),
                longitude=location.get("longitude"),
                latitude=location.get("latitude"),
                creation_time=location.get("creation_time")
            )
            response = stub.Create(location_message)

        except ValidationError as err:
            print(err.messages)