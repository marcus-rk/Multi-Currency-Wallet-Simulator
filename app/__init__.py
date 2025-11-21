# app/__init__.py with create_app()
# setup Flask application factory
from flask import Flask

def create_app(config_class=None): # None for now, should be Config
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    
    # Configure the app (database, blueprints, etc.)
    # init_db(app)
    # register_blueprints(app)

    return app