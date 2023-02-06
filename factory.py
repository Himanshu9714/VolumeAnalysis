from flask import Flask
from flask.logging import default_handler
import logging


def create_app():
    app = Flask(__name__)

    # Configure the app
    configure_app(app)

    # Configure logging
    configure_logging(app)

    # Register APIs
    configure_blueprints(app)

    return app


def configure_app(app):
    """Configure flask application."""
    # load default settings
    app.config.from_object("Analysis.config")


def configure_logging(app):
    """Logging for the flask."""
    # Add default handler.
    app.logger.addHandler(default_handler)

    # Set logging level for flask logger.
    logging_level = app.config["FLASK_LOGLEVEL"]
    if logging_level:
        app.logger.setLevel(getattr(logging, logging_level.upper()))


def configure_blueprints(app):
    """Configure blueprints"""
    from .routes.volumes import api

    # Register the volumes api
    app.register_blueprint(api)
