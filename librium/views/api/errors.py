"""
Error handling utilities for the Librium API.

This module provides utilities for consistent error handling in the API.
"""

from flask import jsonify


def error_response(status_code, message, error_type=None):
    """
    Create a consistent error response.

    Args:
        status_code (int): HTTP status code
        message (str): Error message
        error_type (str, optional): Type of error. If not provided, a default type based on status code is used.

    Returns:
        tuple: JSON response with error details and status code
    """
    # Default error types based on status code
    default_error_types = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
    }

    # Use provided error_type or default based on status code
    if error_type is None:
        error_type = default_error_types.get(status_code, "Error")

    response = {"error": error_type, "message": message, "status_code": status_code}

    return jsonify(response), status_code


def bad_request(message):
    """
    Create a 400 Bad Request error response.

    Args:
        message (str): Error message

    Returns:
        tuple: JSON response with error details and status code 400
    """
    return error_response(400, message)


def unauthorized(message="Authentication required"):
    """
    Create a 401 Unauthorised error response.

    Args:
        message (str, optional): Error message. Defaults to "Authentication required".

    Returns:
        tuple: JSON response with error details and status code 401
    """
    return error_response(401, message)


def forbidden(message="You don't have permission to access this resource"):
    """
    Create a 403 Forbidden error response.

    Args:
        message (str, optional): Error message. Defaults to "You don't have permission to access this resource".

    Returns:
        tuple: JSON response with error details and status code 403
    """
    return error_response(403, message)


def not_found(message="Resource not found"):
    """
    Create a 404 Not Found error response.

    Args:
        message (str, optional): Error message. Defaults to "Resource not found".

    Returns:
        tuple: JSON response with error details and status code 404
    """
    return error_response(404, message)


def method_not_allowed(message="Method not allowed"):
    """
    Create a 405 Method Not Allowed error response.

    Args:
        message (str, optional): Error message. Defaults to "Method not allowed".

    Returns:
        tuple: JSON response with error details and status code 405
    """
    return error_response(405, message)


def conflict(message="Resource already exists"):
    """
    Create a 409 Conflict error response.

    Args:
        message (str, optional): Error message. Defaults to "Resource already exists".

    Returns:
        tuple: JSON response with error details and status code 409
    """
    return error_response(409, message)


def unprocessable_entity(message="Validation error"):
    """
    Create a 422 Unprocessable Entity error response.

    Args:
        message (str, optional): Error message. Defaults to "Validation error".

    Returns:
        tuple: JSON response with error details and status code 422
    """
    return error_response(422, message)


def too_many_requests(message="Too many requests"):
    """
    Create a 429 Too Many Requests error response.

    Args:
        message (str, optional): Error message. Defaults to "Too many requests".

    Returns:
        tuple: JSON response with error details and status code 429
    """
    return error_response(429, message)


def internal_server_error(message="An unexpected error occurred"):
    """
    Create a 500 Internal Server Error error response.

    Args:
        message (str, optional): Error message. Defaults to "An unexpected error occurred".

    Returns:
        tuple: JSON response with error details and status code 500
    """
    return error_response(500, message)
