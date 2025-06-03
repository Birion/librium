"""
API versioning package for Librium.

This package provides versioned API endpoints for the Librium application.
The versioning scheme follows the pattern /api/vX/... where X is the version number.

Current versions:
- v1: Initial API version
"""

from flask import Blueprint, jsonify, request, current_app

# Create the main API blueprint
bp = Blueprint("api", __name__, url_prefix="/api")


# Import and register versioned blueprints
# Import inside a function to avoid circular imports
def _register_versioned_blueprints():
    from librium.views.api.v1 import bp as v1_bp

    bp.register_blueprint(v1_bp)


# Register versioned blueprints
_register_versioned_blueprints()


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
            "documentation": "/api/docs",  # Placeholder for future API documentation
        }
    )


# API error handlers
@bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for API endpoints."""
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested resource was not found",
                "status_code": 404,
            }
        ),
        404,
    )


@bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for API endpoints."""
    return (
        jsonify(
            {
                "error": "Method Not Allowed",
                "message": f"The method {request.method} is not allowed for this endpoint",
                "status_code": 405,
            }
        ),
        405,
    )


@bp.errorhandler(500)
def server_error(error):
    """Handle 500 errors for API endpoints."""
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "status_code": 500,
            }
        ),
        500,
    )
