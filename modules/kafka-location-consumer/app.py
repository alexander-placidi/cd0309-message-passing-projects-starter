import os

from config import config_by_name
from consumer import subscribe

def create_consumer(env=None):
    TOPIC_NAME = config_by_name[env or "test"].KAFKA_TOPIC
    BOOTSTRAP_SERVERS = config_by_name[env or "test"].KAFKA_BOOTSTRAP_SERVERS
    CONSUMER_GROUP_ID = config_by_name[env or "test"].CONSUMER_GROUP_ID
    subscribe(TOPIC_NAME, BOOTSTRAP_SERVERS, CONSUMER_GROUP_ID)


if __name__ == "__main__":
    create_consumer(os.getenv("FLASK_ENV") or "test")