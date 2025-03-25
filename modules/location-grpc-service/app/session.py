import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import config_by_name

env = os.getenv("GRPC_ENV") or "test"
engine = create_engine(config_by_name[env].SQLALCHEMY_DATABASE_URI)
session = Session(engine, expire_on_commit=False)