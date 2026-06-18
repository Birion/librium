# Librium Architecture

## Overview

Librium is a Flask-based web application for managing a personal book library. It follows a layered architecture with clear separation between views, services, and data access.

## Layers

### 1. Views (Presentation)

Flask blueprints handle HTTP requests and render responses. Located in `librium/views/`:

| Blueprint | URL Prefix | Purpose |
|---|---|---|
| `main` | `/` | Home page, statistics |
| `book` | `/book` | Book browsing, detail, filtering |
| `manage` | `/manage` | CRUD management for entities (authors, genres, series, publishers, formats, languages) |
| `covers` | `/covers` | Book cover image serving |
| `api` | `/api` | REST API (v1 sub-blueprint) |
| `swagger_ui` | `/api/docs` | Swagger UI for interactive API docs |

Sub-views in `librium/views/views/` provide additional rendering helpers for authors, books, genres, series, and years.

### 2. Services (Business Logic)

Service classes in `librium/services/` encapsulate business logic and database operations. Each entity has a dedicated service:

- `BookService` — book CRUD, search, pagination, read/unread counts
- `AuthorService` — author management with name parsing
- `GenreService`, `SeriesService`, `PublisherService`, `FormatService`, `LanguageService` — entity CRUD
- `AuthenticationService` — user authentication and password verification
- `YearService` — year-based statistics

Services are stateless and use class methods that operate on SQLAlchemy sessions.

### 3. Database (Data Access)

SQLAlchemy ORM models are defined in `librium/database/sqlalchemy/db.py`. The database layer includes:

- Declarative models with relationships and validation
- Event listeners for automatic timestamp management (`created_at`, `updated_at`)
- Soft-delete support via `deleted_at` column on all entities
- Alembic migrations in `alembic/versions/`

## App Factory

The application is created via `librium.core.app.create_app()`, which:

1. Creates the Flask instance
2. Loads configuration from environment-specific config classes
3. Initializes extensions (Flask-Assets, Flask-Caching, Flask-Compress, JWTManager, Flask-Limiter)
4. Configures Jinja2 environment (custom filters, global variables)
5. Registers all blueprints with rate-limit exemptions
6. Registers error handlers (404, 429, 500, unhandled exceptions)
7. Configures static file cache headers

The app is exposed as `librium:app` for the Flask CLI.

## Extensions

| Extension | Purpose | Configuration |
|---|---|---|
| Flask-Assets | SASS/CoffeeScript compilation | `librium/core/assets.py` |
| Flask-Caching | Response caching (FileSystemCache) | `CACHE_TYPE`, `CACHE_DIR`, `CACHE_DEFAULT_TIMEOUT` |
| Flask-Compress | Gzip compression | `COMPRESS_LEVEL`, `COMPRESS_MIN_SIZE` |
| Flask-JWT-Extended | JWT authentication for API | `JWT_SECRET_KEY`, `JWT_TOKEN_LOCATION` |
| Flask-Limiter | Rate limiting | `librium/core/limit.py` |
| Flask-Swagger-UI | API documentation UI | Served at `/api/docs` |
| Alembic | Database migrations | `alembic.ini`, `alembic/` |
| python-dotenv | Environment variable loading | `.env` file |

## Authentication

- JWT tokens are used for API authentication
- Token endpoint: `POST /api/v1/auth/token`
- Tokens are accepted via `Authorization: Bearer <token>` header or `?token=<token>` query string
- The `Authentication` model stores usernames and bcrypt-hashed passwords

## Rate Limiting

- Global rate limits are applied via Flask-Limiter
- Registered blueprints are exempted from default limits
- Stricter limits apply to:
  - Backup operations: 10/day, 5/hour, 2/minute
  - POST requests to API: 50/day, 20/hour, 3/minute
  - Auth token endpoint: 20/day, 5/hour, 3/minute

## Static Assets

- SASS stylesheets in `librium/static/sass/` (components and partials)
- CoffeeScript in `librium/static/coffee/`
- Compiled bundles output to `librium/static/gen/`
- Cache-control headers set via `after_request` handler (JS/CSS: 1 week, images: 30 days, other: 1 day)

## Logging

- Configured at startup via `librium.core.logging.configure_logging`
- Output to both console and `logs/librium.log`
- Log level controlled by `LOG_LEVEL` environment variable (default: `INFO`)
- Module-specific loggers obtained via `get_logger("module.name")`
