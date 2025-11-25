# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from .config import Config
from .database import init_db, init_schema

def create_app(test_config: dict = None) -> Flask:
    """
    Flask application factory.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    # Ensure instance folder exists (for SQLite file, etc.)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # For tests: allow overriding any config key, including DATABASE
    if test_config is not None:
        app.config.update(test_config)

    init_db(app)

    with app.app_context():
        init_schema()

    # --- Blueprint registration ---
    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    return app
