import os
from app import create_app, config_logger


app = create_app(os.getenv("FLASK_ENV") or "test")
if __name__ == "__main__":
    config_logger()
    app.run(debug=True)