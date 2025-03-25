import os
from app import create_server, config_logger

if __name__ == "__main__":
    config_logger()
    create_server(os.getenv("ENV") or "test")