import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.schemas import ConnectionSchema, LocationSchema, PersonSchema

import grpc
import location_pb2, location_pb2_grpc
import person_pb2_grpc

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        location_channel = grpc.insecure_channel("localhost:5005")
        location_stub = location_pb2_grpc.LocationServiceStub(location_channel)
        person_channel = grpc.insecure_channel("localhost:5005")
        person_stub = person_pb2_grpc.PersonServiceStub(person_channel)
        
        location_message = location_pb2.LocationGetFilteredByDateMessage(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date
        )     
        locations_within_date_range: List = location_stub.GetFilteredByDate(location_message)

        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in person_stub.GetPersons()}

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

        result: List[Connection] = []
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
            ) in location_stub.GetLocationsWithin(location_message):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)

                result.append(
                    Connection(
                        person=person_map[exposed_person_id], location=location,
                    )
                )

        return result
