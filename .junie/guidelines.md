# Librium Development Guidelines

This document consolidates project-specific notes to help advanced contributors work efficiently on Librium.

## Build/Configuration Instructions

### Prerequisites
- Python 3.11 exactly (the codebase and dependencies target 3.11).
- Pipenv for dependency management.

### Install and Run
- Install dependencies and activate the environment:
  - `pip install pipenv`
  - `pipenv install`
  - `pipenv shell`
- Environment variables are loaded from `.env` (python-dotenv is used in app startup):
  - `APPLICATION_NAME=Librium`
  - `DATABASE_URL=sqlite:///librium.sqlite` — SQLAlchemy URI used by the app
  - `FLASK_ENV=development` — or `testing`/`production`
  - `JWT_SECRET_KEY=dev-key-for-local` — required if you touch JWT-protected parts
  - `DEFAULT_CURRENCY=USD` — default currency for book prices
  - Optional: `LIBRIUM_CONFIG=librium.core.config.DevelopmentConfig`

### Notes
- The app uses `DATABASE_URL` mapped to `SQLALCHEMY_DATABASE_URI` in config. Prefer `FLASK_ENV=testing` for in-memory tests.
- Configuration classes (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`) are in `librium/core/config.py`.

### Running the Application
- Development server (uses the app factory wired in `librium.__init__`):
  - `python -m flask --app librium:app run --debug`
- uWSGI (adjust paths in `uwsgi.ini` to match your environment):
  - `uwsgi --ini uwsgi.ini`

## Testing Information

The repo uses `unittest` and SQLAlchemy with an in-memory SQLite option for tests.

### Test Configuration
- In-memory DB via configuration:
  - Set `FLASK_ENV=testing` to get `SQLALCHEMY_DATABASE_URI=sqlite:///:memory:`
- `TestingConfig` also disables caching (`NullCache`) and sets JWT defaults for test environments.

### Caveats
- Creating the full Flask app triggers JWT and rate-limiting configuration. If you are writing unit tests that don't need the HTTP stack, prefer testing pure services/utilities without creating the app to avoid extra setup (JWT_TOKEN_LOCATION, rate limits, etc.).

### Running Tests
- Single test module:
  - `python -m unittest tests/test_models.py -v`
- Single test class or test method:
  - `python -m unittest tests.test_models.TestBook -v`
  - `python -m unittest tests.test_models.TestBook.test_create_book -v`
- Discover all tests (current suite contains unstable tests; prefer targeted runs unless you're working on fixing the suite):
  - `python -m unittest discover -s tests`

### Existing Test Files
- `test_models.py` — ORM model creation and validation
- `test_services.py` — Service layer logic
- `test_api.py` — REST API endpoints
- `test_views.py` — Web UI view functions
- `test_manage.py` — Entity management views
- `test_authors_view.py` — Author-specific views
- `test_filtering.py` — Book filtering and search
- `test_integration.py` — End-to-end integration
- `test_utils.py` — Utility functions

### Adding New Tests
- Place files in `tests/` with the `test_` prefix and `unittest.TestCase` classes.
- Prefer isolated, deterministic tests:
  - For DB tests, create an in-memory engine and `Base.metadata.create_all(engine)`, then use a short-lived `Session` bound to that engine.
  - For API routes, mock service layers and avoid starting the whole app unless you supply JWT and limiter configuration.

## Additional Development Information

### Repository Map
- `librium/core/` — app factory (`app.py`), config, logging, assets, utils, rate limiting (`limit.py`)
- `librium/database/sqlalchemy/db.py` — SQLAlchemy models and `create_tables`
- `librium/services/` — business logic layer (one service per entity: Book, Author, Genre, Series, Publisher, Format, Language, Authentication, Year)
- `librium/views/` — Flask blueprints:
  - `main.py` — home page, statistics
  - `book.py` — book browsing and detail views
  - `manage.py` — entity CRUD management UI (authors, genres, series, publishers, formats, languages)
  - `covers.py` — cover image handling
  - `api/` — REST API blueprint with v1 endpoints and Swagger UI
  - `views/` — sub-views (authors, books, genres, series, years)
- `librium/static/` — assets (SASS, CoffeeScript) bundled via Flask-Assets in `librium/core/assets.py`
- `librium/templates/` — Jinja2 templates (base, book, main, manage, _core)
- `alembic/` — database migration scripts
- `tests/` — unit/integration tests
- `utils/` — standalone utility scripts (export, etc.)

### SQLAlchemy
- Use the SQLAlchemy ORM models in `librium/database/sqlalchemy/db.py`.
- Models: `Book`, `Author`, `Genre`, `Series`, `Publisher`, `Format`, `Language`, `SeriesIndex`, `AuthorOrdering`, `Authentication`
- All entities support soft-delete (`deleted_at`) and automatic timestamp management (`created_at`, `updated_at`).
- For ephemeral tests:
  ```python
  from sqlalchemy import create_engine
  from librium.database.sqlalchemy.db import Base
  from sqlalchemy.orm import Session

  engine = create_engine("sqlite:///:memory:")
  Base.metadata.create_all(engine)
  session = Session(engine)
  ```

### App/Blueprints
- The app factory is `librium.core.app.create_app` and is exposed as `librium:app` for Flask CLI.
- Blueprints registered: `main`, `book`, `manage`, `covers`, `api` (with v1 sub-blueprint), `swagger_ui`.
- Rate limiting is applied globally via `librium.core.limit.limiter` (exempted for registered blueprints during init).

### Auth/JWT
- `JWTManager` is initialised in `create_app`. If a test or script exercises endpoints that require JWT, set at least `JWT_SECRET_KEY` and, if needed, `JWT_TOKEN_LOCATION` and related claims in `app.config`.
- Tokens accepted via `Authorization: Bearer <token>` header or `?token=<token>` query string.
- Auth token endpoint: `POST /api/v1/auth/token`

### REST API (v1)
- All API endpoints require JWT authentication (`@jwt_required()`).
- Key endpoints: `/api/v1/books`, `/api/v1/add`, `/api/v1/delete`, `/api/v1/series`, `/api/v1/genres`, `/api/v1/languages`, `/api/v1/publishers`, `/api/v1/export`, `/api/v1/backup/*`
- Request validation via `webargs` with schemas in `librium/views/api/v1/schemas.py`.
- Swagger UI available at `/api/docs`.

### Logging
- Logging is configured at startup (`librium.core.logging.configure_logging`). Adjust via `LOG_LEVEL` env var; output goes to `logs/librium.log` in addition to console.
- Use `get_logger("module.name")` for module-specific loggers.

### Assets
- Flask-Compress is enabled; cache-control headers are set for static content via an `after_request` handler.
- Generated bundles live under `librium/static/gen`.
- SASS partials in `librium/static/sass/partials/`, components in `librium/static/sass/components/`.

### Code Style
- Python: PEP 8; type hints used in core modules.
- No `print()` in non-test code; use logging.
- Keep view logic thin; push business logic to services.
- Templates: consistent indentation; custom Jinja filter `parse_read_arg` is registered.

### Debugging Tips
- Run with `--debug` to get better tracebacks and use the dev favicon.
- For DB issues, enable SQL echo on temporary engines (`create_engine("sqlite:///:memory:", echo=True)`).
- When diagnosing API failures under tests, watch for missing JWT and limiter config causing early failures.
