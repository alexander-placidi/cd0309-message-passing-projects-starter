import os
from app import create_app, config_logger
from app.config import config_by_name

config = config_by_name[os.getenv("FLASK_ENV") or "test"]

app = create_app(os.getenv("FLASK_ENV") or "test")
if __name__ == "__main__":
    config_logger()
    server_host = config.SERVER_HOST
    server_port = config.SERVER_PORT
    
    app.run(debug=True, host=server_host, port=server_port)