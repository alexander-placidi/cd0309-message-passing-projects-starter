import os

from app.config import config_by_name
from app import create_consumer, config_logger


if __name__ == "__main__":
    config_logger()
    create_consumer(os.getenv("ENV") or "test")