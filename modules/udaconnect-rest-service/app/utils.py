from datetime import datetime
from proto import location_pb2, person_pb2
from app.dataclasses import Location, Person

str_to_datetime = lambda dt_str: datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
datetime_to_str = lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")

def location_protobuf_to_class(protobuf: location_pb2.LocationMessage) -> Location:
    return Location(
        id=int(protobuf.location_id),
        person_id=int(protobuf.person_id),
        longitude=protobuf.longitude,
        latitude=protobuf.latitude,
        creation_time=str_to_datetime(protobuf.creation_time)
    )

def person_protobuf_to_class(protobuf: person_pb2.PersonMessage) -> Person:
    return Person(
        id=protobuf.person_id,
        first_name=protobuf.first_name,
        last_name=protobuf.last_name,
        company_name=protobuf.company_name
    )