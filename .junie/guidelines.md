# Librium Development Guidelines

This document consolidates project-specific notes to help advanced contributors work efficiently on Librium.

## Build/Configuration Instructions

### Prerequisites
- Python 3.11 exactly (the codebase and dependencies target 3.11).
- Pipenv for dependency management.

### Install and Run
- Install dependencies and activate the environment:
  - pip install pipenv
  - pipenv install
  - pipenv shell
- Environment variables are loaded from .env (python-dotenv is used in app startup):
  - APPLICATION_NAME=Librium
  - DATABASE_URL=sqlite:///librium.sqlite  # SQLAlchemy URI used by the app
  - FLASK_ENV=development                   # or testing/production
  - JWT_SECRET_KEY=dev-key-for-local        # required if you touch JWT-protected parts
  - Optional: LIBRIUM_CONFIG=librium.core.config.DevelopmentConfig

Notes
- The older SQLDATABASE variable is referenced by some legacy tests/docs; the running app uses DATABASE_URL/SQLALCHEMY_DATABASE_URI. Prefer FLASK_ENV=testing for in-memory tests.

### Running the Application
- Development server (uses the app factory already wired in librium.__init__):
  - python -m flask --app librium:app run --debug
- uWSGI (adjust paths in uwsgi.ini to match your environment):
  - uwsgi --ini uwsgi.ini

## Testing Information

The repo uses unittest and SQLAlchemy with an in-memory SQLite option for tests.

### Test Configuration
- In-memory DB via configuration:
  - Set FLASK_ENV=testing to get SQLALCHEMY_DATABASE_URI=sqlite:///:memory:
- Alternatively, tests that construct their own Engine can set SQLDATABASE or engine explicitly. Example pattern used in the suite:
  - import os; os.environ["SQLDATABASE"] = ":memory:"

Caveats
- Creating the full Flask app triggers JWT and rate-limiting configuration. If you are writing unit tests that don’t need the HTTP stack, prefer testing pure services/utilities without creating the app to avoid extra setup (JWT_TOKEN_LOCATION, rate limits, etc.).

### Running Tests
- Single test module:
  - python -m unittest tests/test_models.py -v
- Single test class or test method:
  - python -m unittest tests.test_models.TestBook -v
  - python -m unittest tests.test_models.TestBook.test_create_book -v
- Discover all tests (current suite contains unstable tests; prefer targeted runs unless you’re working on fixing the suite):
  - python -m unittest discover -s tests

### Adding New Tests
- Place files in tests/ with the test_ prefix and unittest.TestCase classes.
- Prefer isolated, deterministic tests:
  - For DB tests, create an in-memory engine and Base.metadata.create_all(engine), then use a short-lived Session bound to that engine.
  - For API routes, mock service layers and avoid starting the whole app unless you supply JWT and limiter configuration.

### Demo: a minimal test you can run now
This test was executed successfully during guideline preparation and demonstrates the local test workflow without app setup.

File: tests/test_smoke.py

"""
A simple, isolated smoke test to demonstrate how to add and run a test in Librium.
This test avoids creating the full Flask app and external services; it only tests
pure utility logic.
"""

```python
import unittest

from librium.core.utils import parse_read_arg


class TestSmoke(unittest.TestCase):
    def test_parse_read_arg_rotation(self):
        # None -> interpreted as 'all' -> next is 'unread' with URL param 0
        next_status, url_param = parse_read_arg(None)
        self.assertEqual(next_status, "unread")
        self.assertEqual(url_param, 0)

        # 'unread' (0/False) -> next is 'read' with URL param 1
        next_status, url_param = parse_read_arg(0)
        self.assertEqual(next_status, "read")
        self.assertEqual(url_param, 1)

        # 'read' (1 or "true") -> next is 'all' with URL param None
        next_status, url_param = parse_read_arg(1)
        self.assertEqual(next_status, "all")
        self.assertIsNone(url_param)


if __name__ == "__main__":
    unittest.main()
```

Run it:
- python -m unittest tests/test_smoke.py -v

Note: This file is provided as an example in the documentation only. Do not commit it as a permanent test if you are not maintaining it.

## Additional Development Information

### Repository Map
- librium/core/: app factory, config, logging, assets, utils
- librium/database/sqlalchemy/db.py: SQLAlchemy models and create_tables
- librium/views/: Flask blueprints (views/ and api/)
- librium/static/: assets (SASS, CoffeeScript) bundled via Flask-Assets in librium/core/assets.py
- tests/: unit/integration tests (current coverage is mixed and in progress)

### SQLAlchemy
- Use the SQLAlchemy ORM models in librium/database/sqlalchemy/db.py. For ephemeral tests:
  - from sqlalchemy import create_engine
  - engine = create_engine("sqlite:///:memory:")
  - Base.metadata.create_all(engine)
  - session = Session(engine)

### App/Blueprints
- The app factory is librium.core.app.create_app and is exposed as librium:app for Flask CLI.
- Blueprints are registered in create_app; rate limiting is applied globally via librium.core.limit.limiter (exempted for registered blueprints during init).

### Auth/JWT
- JWTManager is initialised in create_app. If a test or script exercises endpoints that require JWT, set at least JWT_SECRET_KEY and, if needed, JWT_TOKEN_LOCATION and related claims in app.config.

### Logging
- Logging is configured at startup (librium.core.logging.configure_logging). Adjust via LOG_LEVEL env var; output goes to logs/librium.log in addition to console.

### Assets
- Flask-Compress is enabled; cache-control headers are set for static content via an after_request handler. Generated bundles live under librium/static/gen.

### Code Style
- Python: PEP 8; type hints used in core modules.
- Templates: consistent indentation; custom Jinja filter parse_read_arg is registered.
- CSS/SASS: split into components and partials.

### Debugging Tips
- Run with --debug to get better tracebacks and use the dev favicon.
- For DB issues, enable SQL echo on temporary engines (create_engine("sqlite:///:memory:", echo=True)).
- When diagnosing API failures under tests, watch for missing JWT and limiter config causing early failures.
