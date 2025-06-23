# Rate limiting setup
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)

# Apply rate limiting to API endpoints with different limits for different endpoints

# More restrictive limits for authentication endpoint to prevent brute force attacks
limiter.limit("20/day;5/hour;3/minute", override_defaults=True)(
    lambda: request.path.startswith("/api/v1/auth/")
)

# More restrictive limits for backup operations (resource-intensive)
limiter.limit("10/day;5/hour;2/minute", override_defaults=True)(
    lambda: request.path.startswith("/api/v1/backup/")
)

# More restrictive limits for data modification endpoints (POST methods)
limiter.limit("50/day;20/hour;3/minute", override_defaults=True)(
    lambda: request.method == "POST" and request.path.startswith("/api/v1/")
)
