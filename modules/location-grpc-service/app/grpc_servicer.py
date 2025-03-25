from typing import List
from datetime import datetime

from app.services import LocationService
from proto import location_pb2, location_pb2_grpc
from app.models import Location


class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Get(self, request, context):
        id = request.location_id
        location: Location = LocationService.retrieve(location_id=id)
        location_message = location_pb2.LocationMessage(
            location_id=int(location.id),
            person_id=int(location.person_id),
            longitude=location.longitude,
            latitude=location.latitude,
            creation_time=location.creation_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        return location_message


    def GetContacts(self, request, context):
        locations: List[Location] = LocationService.retrieveContactLocations(
            person_id=request.person_id,
            start_date=datetime.strptime(request.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(request.end_date, "%Y-%m-%d"),
            meters=request.meters
        )

        locations_message = location_pb2.LocationMessageList()
        for location in locations:
            location_message = location_pb2.LocationMessage(
                location_id=int(location.id),
                person_id=int(location.person_id),
                longitude=location.longitude,
                latitude=location.latitude,
                creation_time=location.creation_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            locations_message.locations.append(location_message)

        return locations_message


    def Create(self, request, context):
        location_request = {
            "id": request.location_id,
            "person_id": request.person_id,
            "longitude": request.longitude,
            "latitude": request.latitude,
            "creation_time": request.creation_time
        }
        location = LocationService.create(location_request)

        return location_pb2.LocationMessage(
            location_id=location.id,
            person_id=location.person_id,
            longitude=location.longitude,
            latitude=location.latitude,
            creation_time=location.creation_time #.strftime("%Y-%m-%d %H:%M:%S")
        )