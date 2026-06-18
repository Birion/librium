# Contributing to Librium

Thanks for your interest in contributing! This guide explains how to set up the project, follow our standards, and submit changes effectively.

## Getting Started

### 1. Environment

- **Python:** 3.11 exactly
- **Dependency manager:** Pipenv
- **OS:** Cross-platform; dev notes assume Unix-like or Windows PowerShell

### 2. Setup

```bash
pip install pipenv
pipenv install
pipenv shell
```

Create a `.env` file in the project root (or copy `.env.example` if available). Common variables:

```
APPLICATION_NAME=Librium
DATABASE_URL=sqlite:///librium.sqlite
FLASK_ENV=development
JWT_SECRET_KEY=dev-key-for-local
```

Set `FLASK_ENV=testing` for in-memory SQLite during tests.

### 3. Running the Application

```bash
# Development server with hot-reload
python -m flask --app librium:app run --debug
```

For production deployment with uWSGI, adjust paths in `uwsgi.ini` and run:

```bash
uwsgi --ini uwsgi.ini
```

## Branching and Commits

- Branch from `main`: `feature/<short-topic>` or `fix/<short-topic>`
- Keep commits focused and messages in imperative mood: "Add X", "Fix Y"
- Reference issues/tasks when relevant

## Code Style

- **Python:** PEP 8; type hints used in core modules
- No `print()` in non-test code; use `logging` via `librium.core.logging.get_logger`
- Keep view logic thin; push business logic into the service layer (`librium/services/`)
- Small, focused functions; prefer clarity over cleverness

## Database

- Use SQLAlchemy ORM models defined in `librium/database/sqlalchemy/db.py`
- Models: `Book`, `Author`, `Genre`, `Series`, `Publisher`, `Format`, `Language`, `SeriesIndex`, `AuthorOrdering`, `Authentication`
- All entities support soft-delete (via `deleted_at` timestamp) and automatic `created_at`/`updated_at` tracking
- For schema changes, create Alembic migrations (`alembic/versions/`) and test against both SQLite and in-memory SQLite

## Testing

The project uses `unittest` with SQLAlchemy and in-memory SQLite.

### Running Tests

```bash
# Single test module
python -m unittest tests/test_models.py -v

# Single test class or method
python -m unittest tests.test_models.TestBook -v
python -m unittest tests.test_models.TestBook.test_create_book -v

# Discover all tests (some tests may be unstable; prefer targeted runs)
python -m unittest discover -s tests
```

### Writing Tests

- Place files in `tests/` with the `test_` prefix and `unittest.TestCase` classes
- Prefer isolated, deterministic tests:
  - For DB tests, create an in-memory engine and `Base.metadata.create_all(engine)`, then use a short-lived `Session` bound to that engine
  - For API routes, mock service layers and avoid starting the whole app unless you supply JWT and limiter configuration
- Creating the full Flask app triggers JWT and rate-limiting setup. If you are writing unit tests that don't need the HTTP stack, prefer testing pure services/utilities without creating the app

### Existing Test Files

| File                   | Coverage                          |
|------------------------|-----------------------------------|
| `test_models.py`       | ORM model creation and validation |
| `test_services.py`     | Service layer logic               |
| `test_api.py`          | REST API endpoints                |
| `test_views.py`        | Web UI view functions             |
| `test_manage.py`       | Entity management views           |
| `test_authors_view.py` | Author-specific views             |
| `test_filtering.py`    | Book filtering and search         |
| `test_integration.py`  | End-to-end integration            |
| `test_utils.py`        | Utility functions                 |

## Documentation

- Update documentation alongside code changes (APIs, DB schema, behaviour changes)
- Keep changelog entries in PR descriptions when relevant
- Documentation files:
  - `README.md` — project overview, setup, and API reference
  - `CONTRIBUTING.md` — this file
  - `docs/` — additional documentation (architecture, database schema)

## Pull Requests

- Include a clear summary of changes and rationale
- Note any migrations or breaking changes
- Add screenshots for UI changes
- Ensure linters/tests pass; include steps to reproduce fixes where applicable

## Code Review

- Be respectful and constructive
- Review for clarity, correctness, and consistency
- Prefer suggestions with examples

## Security

- Do not commit secrets; use environment variables
- Report security concerns privately to maintainers

## License

By contributing, you agree your contributions are licensed under the project's [MIT Licence](LICENSE).

Thank you for helping improve Librium!
