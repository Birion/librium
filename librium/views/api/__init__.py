"""
API versioning package for Librium.

This package provides versioned API endpoints for the Librium application.
The versioning scheme follows the pattern /api/vX/... where X is the version number.

Current versions:
- v1: Initial API version
"""

from flask import Blueprint, jsonify, request, current_app

# Import Swagger documentation
from librium.views.api.swagger import swagger_ui_blueprint, swagger_spec

# Import error handling utilities
from librium.views.api.errors import (
    not_found,
    method_not_allowed,
    internal_server_error,
)

# Create the main API blueprint
bp = Blueprint("api", __name__, url_prefix="/api")


# Import and register versioned blueprints
# Import inside a function to avoid circular imports
def _register_versioned_blueprints():
    from librium.views.api.v1 import bp as v1_bp

    bp.register_blueprint(v1_bp)


# Register versioned blueprints
_register_versioned_blueprints()

# Register Swagger UI blueprint
bp.register_blueprint(swagger_ui_blueprint)


# Swagger specification endpoint
@bp.route("/swagger.json", methods=["GET"])
def swagger_json():
    """
    Return the Swagger specification as JSON.

    Returns:
        JSON response with the Swagger specification
    """
    return jsonify(swagger_spec)


# API information endpoint
@bp.route("/", methods=["GET"])
def api_info():
    """
    Return information about the API.

    Returns:
        JSON response with API information
    """
    return jsonify(
        {
            "name": "Librium API",
            "version": current_app.config["VERSION"],
            "available_versions": ["v1"],
            "documentation": "/api/docs",  # Swagger documentation URL
        }
    )


# API error handlers
@bp.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors for API endpoints."""
    return not_found("The requested resource was not found")


@bp.errorhandler(405)
def handle_method_not_allowed(error):
    """Handle 405 errors for API endpoints."""
    return method_not_allowed(
        f"The method {request.method} is not allowed for this endpoint"
    )


@bp.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors for API endpoints."""
    return internal_server_error("An unexpected error occurred")
