import json, grpc, os, logging
from marshmallow import ValidationError, EXCLUDE
from kafka import KafkaConsumer

from app.schemas import LocationSchema
from app.config import config_by_name
from proto import location_pb2
from proto import location_pb2_grpc
from app.errors import log_grpc_error

@staticmethod
def subscribe(kafka_topic:str, kafka_bootstrap_servers: list[str], consumer_group_id: str) -> None:
    consumer = KafkaConsumer(
        kafka_topic, 
        bootstrap_servers=kafka_bootstrap_servers, 
        group_id=consumer_group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    config = config_by_name[os.getenv("FLASK_ENV") or "test"]
    channel = grpc.insecure_channel(f"{config.GRPC_LOCATION_SERVICE_HOST}:{config.GRPC_LOCATION_SERVICE_PORT}")
    stub = location_pb2_grpc.LocationServiceStub(channel)
    for message in consumer:
        logging.info(
            f"""
            Received message on topic {message.topic}:
            Key: {message.key}
            Value: {message.value}
            """
        )
        
        schema = LocationSchema()
        try:
            location = schema.load(message.value, unknown=EXCLUDE)
            location_message = location_pb2.LocationMessage(
                location_id=location.get("id"),
                person_id=location.get("person_id"),
                longitude=location.get("longitude"),
                latitude=location.get("latitude"),
                creation_time=location.get("creation_time").strftime("%Y-%m-%d %H:%M:%S")
            )
            response = stub.Create(location_message)

        except ValidationError as err:
            logging.error(err.messages())
        except grpc.RpcError as rpc_error:
            log_grpc_error(rpc_error)