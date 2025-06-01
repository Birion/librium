import os
import os.path
from dotenv import find_dotenv, load_dotenv
from flask import Flask, url_for, request
from pony.flask import Pony
from librium.__version__ import __version__
from librium.views import book, main, api, covers
from librium.core.assets import assets
from librium.core.utils import parse_read_arg

# Constants
FLASK_APP_NAME = "librium"
FAVICON_PATH = "img/favicon.ico"

load_dotenv(find_dotenv())


def configure_flask_app(app: Flask) -> None:
    """Configure basic Flask application settings."""
    app.config["VERSION"] = __version__


def configure_jinja_env(app: Flask) -> None:
    """Configure Jinja environment settings and filters."""
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.filters["parse_read_arg"] = parse_read_arg
    app.jinja_env.globals.update(
        {
            "url_for_self": create_url_for_self,
            "version": __version__,
            "app_name": os.getenv("APPLICATION_NAME"),
        }
    )


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    blueprints = [main.bp, book.bp, api.bp, covers.bp]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def create_url_for_self(**args):
    """Create URL for the current endpoint with updated arguments."""
    return url_for(request.endpoint, **dict(request.args, **args))


def handle_favicon(app):
    """Handle favicon.ico requests."""
    return app.send_static_file(FAVICON_PATH)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(FLASK_APP_NAME)

    # Initialize extensions
    Pony().init_app(app)
    assets.init_app(app)

    # Configure application
    configure_flask_app(app)
    configure_jinja_env(app)

    # Register routes and blueprints
    app.route("/favicon.ico")(lambda: handle_favicon(app))
    register_blueprints(app)

    return app
