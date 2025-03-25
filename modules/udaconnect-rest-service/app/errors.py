import logging

def log_grpc_error(error):
    status_code = error.code()
    logging.error(
    f"""gRPC error: {error.details()}
    Status: {status_code.name} {status_code.value}
    """
    )
