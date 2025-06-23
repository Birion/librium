from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, url_for, jsonify
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter

from librium.__version__ import __version__
from librium.core.assets import assets
from librium.core.config import get_config
from librium.core.logging import configure_logging, get_logger
from librium.core.utils import parse_read_arg
from librium.core.limit import limiter
from librium.views import book, covers, main
from librium.views.api import bp as api_bp
from librium.views.api.errors import too_many_requests
from librium.views.api.swagger import swagger_ui_blueprint

# Constants
FLASK_APP_NAME = "librium"
FAVICON_PATH = "img/favicon.ico"

# Load environment variables
load_dotenv(find_dotenv())

# Get logger for this module
logger = get_logger("core.app")


def configure_flask_app(app: Flask) -> None:
    """Configure basic Flask application settings."""
    # Get the appropriate configuration based on the environment
    config_class = get_config()
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(log_level=app.config.get("LOG_LEVEL"))

    # Set version
    app.config["VERSION"] = __version__

    logger.info(f"Using configuration: {config_class.__name__}")


def configure_jinja_env(app: Flask) -> None:
    """Configure Jinja environment settings and filters."""
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.filters["parse_read_arg"] = parse_read_arg
    app.jinja_env.globals.update(
        {
            "url_for_self": create_url_for_self,
            "version": __version__,
            "app_name": app.config.get("APPLICATION_NAME"),
        }
    )


def register_blueprints(app: Flask, limiter: Limiter) -> None:
    """Register all application blueprints."""
    blueprints = [main.bp, book.bp, api_bp, swagger_ui_blueprint, covers.bp]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        limiter.exempt(blueprint)


def create_url_for_self(**args):
    """Create URL for the current endpoint with updated arguments."""
    return url_for(request.endpoint, **dict(request.args, **args))


def handle_favicon(app):
    """Handle favicon.ico requests."""
    return app.send_static_file(FAVICON_PATH)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""

    @app.errorhandler(404)
    def page_not_found(error):
        """Handle 404 errors."""
        logger.warning(f"404 error: {request.path} - {error}")
        return (
            render_template("_core/error.html", error=error, code=404, debug=app.debug),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors."""
        logger.error(f"500 error: {request.path} - {error}")
        return (
            render_template("_core/error.html", error=error, code=500, debug=app.debug),
            500,
        )

    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {request.path} - {e}")
        return too_many_requests("Too many requests. Please try again later.")

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unhandled exceptions."""
        logger.exception(f"Unhandled exception: {error}")
        return (
            render_template("_core/error.html", error=error, code=500, debug=app.debug),
            500,
        )


def create_app():
    """Create and configure the Flask application."""
    app = Flask(FLASK_APP_NAME)

    # Initialise extensions
    assets.init_app(app)

    # Configure application
    configure_flask_app(app)
    configure_jinja_env(app)

    # JWT setup
    jwt = JWTManager(app)

    # Rate limiting setup
    limiter.init_app(app)

    # Register routes and blueprints
    app.route("/favicon.ico")(lambda: handle_favicon(app))
    register_blueprints(app, limiter)

    # Register error handlers
    register_error_handlers(app)

    logger.info(f"Application {FLASK_APP_NAME} v{__version__} created")

    return app
