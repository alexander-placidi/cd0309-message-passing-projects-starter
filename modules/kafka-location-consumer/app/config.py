import os
from typing import List, Type
from environs import env

class BaseConfig:
    CONFIG_NAME = "base"
    USE_MOCK_EQUIVALENCY = False
    DEBUG = False
    GRPC_LOCATION_SERVICE_HOST = env("GRPC_LOCATION_SERVICE_HOST")
    GRPC_LOCATION_SERVICE_PORT = env("GRPC_LOCATION_SERVICE_PORT")
    KAFKA_BOOTSTRAP_SERVERS = env.list("KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC = env("KAFKA_TOPIC")
    KAFKA_CONSUMER_GROUP_ID = env("KAFKA_CONSUMER_GROUP_ID")

class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )
    DEBUG = True
    TESTING = False
    

class TestingConfig(BaseConfig):
    CONFIG_NAME = "test"
    SECRET_KEY = os.getenv("TEST_SECRET_KEY", "Thanos did nothing wrong")
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    CONFIG_NAME = "prod"
    SECRET_KEY = os.getenv("PROD_SECRET_KEY", "I'm Ron Burgundy?")
    DEBUG = False
    TESTING = False
    

EXPORT_CONFIGS: List[Type[BaseConfig]] = [
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
]
config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}
