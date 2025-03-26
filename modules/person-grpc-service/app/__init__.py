import logging, sys, grpc, os
from concurrent import futures
from app.grpc_servicer import PersonServicer
from proto import person_pb2_grpc
from app.config import config_by_name


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
    

def create_server(env=None):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServicer(), server)

    grpc_port = config_by_name[os.getenv("ENV") or "test"].GRPC_PORT
    logging.info(f"Server starting on port {grpc_port}...")
    
    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)