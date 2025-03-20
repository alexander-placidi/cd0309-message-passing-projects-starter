def create_app(env=None):
    from config import config_by_name

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