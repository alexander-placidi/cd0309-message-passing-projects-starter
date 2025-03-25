import logging, sys

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api

def create_app(env=None):
    from app.config import config_by_name

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="UdaConnect API", version="0.1.0")

    CORS(app)  # Set CORS for development

    register_routes(api, app)

    @app.route("/health")
    def health():
        return jsonify("healthy")

    return app


def register_routes(api, app, root="api"):
    from app.controllers import api as udaconnect_api

    api.add_namespace(udaconnect_api, path=f"/{root}")


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