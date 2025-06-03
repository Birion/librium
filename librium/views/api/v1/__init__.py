"""
API v1 package for Librium.

This package provides the v1 API endpoints for the Librium application.
"""

from flask import Blueprint

# Create the v1 API blueprint
bp = Blueprint("api_v1", __name__, url_prefix="/v1")

# Import API endpoints
from librium.views.api.v1.endpoints import *
