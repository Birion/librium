"""
API module for Librium (Legacy).

This module is deprecated and will be removed in a future version.
Please use the versioned API modules instead:
- librium.views.api.v1

This module provides a blueprint for backward compatibility.
"""

import warnings
from flask import Blueprint

# Create a blueprint for backward compatibility
bp = Blueprint("api", __name__, url_prefix="/api")

# Show deprecation warning
warnings.warn(
    "The librium.views.api module is deprecated and will be removed in a future version. "
    "Please use the versioned API modules instead (librium.views.api.v1).",
    DeprecationWarning,
    stacklevel=2,
)


# The actual API implementation has been moved to versioned modules.
# See librium.views.api.v1.endpoints for the current implementation.
