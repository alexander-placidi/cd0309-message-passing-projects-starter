import logging, os 
from typing import Dict, List

from config import config_by_name
from models import Location
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine

from schemas import LocationSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

env = os.getenv("GRPC_ENV") or "test"
engine = create_engine(config_by_name[env].SQLALCHEMY_DATABASE_URI)

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        session = Session(engine)
        location, coord_text = (
            session.execute(select(Location, Location.coordinate.ST_AsText()))
            .where(Location.id == location_id)
            .first()
        )
        session.close()

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location
    
    @staticmethod
    def retrieveByDateRange(*, person_id, start_date, end_date) -> List[Location]:
        session = Session(engine)
        locations = (
            session.execute(select(Location))
            .where(Location.person_id == person_id)
            .where(Location.creation_time < end_date)
            .where(Location.creation_time >= start_date)
            .fetchall()
        )
        session.close()

        return locations
    
    @staticmethod
    def retrieveWithin(*, person_id, longitude, latitude, meters, start_date, end_date) -> List[Location]:
        session = Session(engine)
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
        params = {
            person_id: person_id,
            longitude: longitude,
            latitude: latitude,
            meters: meters,
            start_date: start_date,
            end_date: end_date
        }
        locations = session.execute(query, params)
        session.close()

        return locations

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
       
        session = Session(engine)
        session.add(new_location)
        session.commit()
        session.close()

        return new_location
