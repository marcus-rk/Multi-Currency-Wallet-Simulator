# setup Flask application factory
from flask import Flask
from .config import Config
from .database import init_db

def create_app(test_config: dict | None = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # DB teardown hook
    init_db(app)

    # Register blueprints
    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    return app