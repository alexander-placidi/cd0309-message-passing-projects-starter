import os
from typing import List, Type

GRPC_PERSON_SERVICE_PORT = os.environ["GRPC_PERSON_SERVICE_PORT"]
GRPC_LOCATION_SERVICE_PORT = os.environ["GRPC_LOCATION_SERVICE_PORT"]

class BaseConfig:
    CONFIG_NAME = "base"
    USE_MOCK_EQUIVALENCY = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )
    DEBUG = True
    TESTING = False
    GRPC_PERSON_SERVICE_PORT=GRPC_PERSON_SERVICE_PORT
    GRPC_LOCATION_SERVICE_PORT=GRPC_LOCATION_SERVICE_PORT

class TestingConfig(BaseConfig):
    CONFIG_NAME = "test"
    SECRET_KEY = os.getenv("TEST_SECRET_KEY", "Thanos did nothing wrong")
    DEBUG = True
    TESTING = True
    GRPC_PERSON_SERVICE_PORT=GRPC_PERSON_SERVICE_PORT
    GRPC_LOCATION_SERVICE_PORT=GRPC_LOCATION_SERVICE_PORT


class ProductionConfig(BaseConfig):
    CONFIG_NAME = "prod"
    SECRET_KEY = os.getenv("PROD_SECRET_KEY", "I'm Ron Burgundy?")
    DEBUG = False
    TESTING = False
    GRPC_PERSON_SERVICE_PORT=GRPC_PERSON_SERVICE_PORT
    GRPC_LOCATION_SERVICE_PORT=GRPC_LOCATION_SERVICE_PORT


EXPORT_CONFIGS: List[Type[BaseConfig]] = [
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
]
config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}
