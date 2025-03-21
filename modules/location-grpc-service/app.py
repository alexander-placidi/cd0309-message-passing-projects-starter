import time, os
from concurrent import futures
from typing import List

import grpc
import location_pb2
import location_pb2_grpc

from services import LocationService
from models import Location
from config import config_by_name


class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Get(self, request, context):
        id = request.id
        location: Location = LocationService.retrieve(location_id=id)
        location_message = location_pb2.LocationMessage(
            location_id=location.id,
            person_id=location.person_id,
            longitude=location.longitude,
            latitude=location.latitude,
            creation_time=location.creation_time
        )
        return location_message   

    def GetFilteredByDate(self, request, context):
        locations: List[Location] = LocationService.retrieveByDateRange(
            person_id=request.person_id,
            start_date=request.start_date,
            end_date=request.end_date
        )

        locations_message = location_pb2.LocationMessageList()
        for location in locations:
            location_message = location_pb2.LocationMessage(
                location_id=location.id,
                person_id=location.person_id,
                longitude=location.longitude,
                latitude=location.latitude,
                creation_time=location.creation_time
            )
            locations_message.locations.append(location_message)

        return locations_message 


    def GetLocationsWithin(self, request, context):
        locations: List[Location] = LocationService.retrieveWithin(
            person_id=request.person_id,
            longitude=request.longitude,
            latitude=request.latitude,
            meters=request.meters,
            start_date=request.start_date,
            end_date=request.end_date
        )

        locations_message = location_pb2.LocationMessageList()
        for location in locations:
            location_message = location_pb2.LocationMessage(
                location_id=location.id,
                person_id=location.person_id,
                longitude=location.longitude,
                latitude=location.latitude,
                creation_time=location.creation_time
            )
            locations_message.locations.append(location_message)

        return locations_message


    def Create(self, request, context):
        location_request = {
            "id": request.id,
            "person_id": request.person_id,
            "longitude": request.longitude,
            "latitude": request.latitude,
            "creation_time": request.creation_time
        }
        location: Location = LocationService.create(location_request)

        return location_pb2_grpc.LocationMessage(
            location_id=location.id,
            person_id=location.person_id,
            longitude=location.longitude,
            latitude=location.latitude,
            creation_time=location.creation_time
        )


server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

grpc_port = config_by_name[os.getenv("FLASK_ENV") or "test"].GRPC_PORT
print(f"Server starting on port {grpc_port}...")
server.add_insecure_port(f"[::]:{grpc_port}")
server.start()
# Keep thread alive
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    server.stop(0)