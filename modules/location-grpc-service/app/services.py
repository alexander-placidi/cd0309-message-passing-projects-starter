import logging
from typing import Dict, List
from datetime import datetime, timedelta

from geoalchemy2.functions import ST_Point
from sqlalchemy.sql import text
from sqlalchemy import select

from app.models import Location
from app.schemas import LocationSchema
from app.session import session


class LocationService:
    @staticmethod
    def retrieve(location_id: int) -> Location:
        location= (
            session.execute(
                select(Location, Location.coordinate.ST_AsText())
                .where(Location.id == location_id)
            ).scalar_one()
        )

        return location
    
    
    @staticmethod
    def retrieveContactLocations(*, person_id: int, start_date: datetime, end_date: datetime, meters: int) -> List[Location]:
        locations = (
            session.execute(
                select(Location)
                .where(Location.person_id == person_id)
                .where(Location.creation_time < end_date)
                .where(Location.creation_time >= start_date)          
            ).scalars().all() 
        )

        data = []
        for location in locations:
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

        query = text(
            """
            SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
            FROM    location
            WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
            AND     person_id != :person_id
            AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
            AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
            """
        )

        locations: List[Location] = []

        for line in tuple(data):
            locs = session.execute(query, line)
            for (exposed_person_id, location_id, exposed_lat, exposed_long, exposed_time) in locs:
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)
                locations.append(location)
        
        return locations

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logging.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        new_location = Location()
        new_location.id = location["id"]
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
       
        session.add(new_location)
        session.commit()

        return new_location
