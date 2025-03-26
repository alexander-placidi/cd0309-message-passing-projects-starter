import logging, sys
from app.config import config_by_name
from app.consumer import subscribe

def create_consumer(env=None):
    TOPIC_NAME = config_by_name[env or "test"].KAFKA_TOPIC
    BOOTSTRAP_SERVERS = config_by_name[env or "test"].KAFKA_BOOTSTRAP_SERVERS
    CONSUMER_GROUP_ID = config_by_name[env or "test"].KAFKA_CONSUMER_GROUP_ID
    subscribe(TOPIC_NAME, BOOTSTRAP_SERVERS, CONSUMER_GROUP_ID)


def config_logger():
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s from %(funcName)s'
    
    console_stdout_handler = logging.StreamHandler(sys.stdout)
    console_stderr_handler = logging.StreamHandler(sys.stderr)
    
    console_stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    console_stderr_handler.addFilter(lambda record: record.levelno > logging.INFO)

    handlers =[console_stdout_handler, console_stderr_handler]
    
    logging.basicConfig(
        level=logging.DEBUG, 
        format=FORMAT,
        handlers=handlers)