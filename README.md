```text
██╗     ██╗██████╗ ██████╗ ██╗██╗   ██╗███╗   ███╗
██║     ██║██╔══██╗██╔══██╗██║██║   ██║████╗ ████║
██║     ██║██████╔╝██████╔╝██║██║   ██║██╔████╔██║
██║     ██║██╔══██╗██╔══██╗██║██║   ██║██║╚██╔╝██║
███████╗██║██████╔╝██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

**Librium** is a personal book library manager built with Flask and SQLAlchemy. It provides a web UI for browsing, filtering, and managing your book collection, along with a JWT-protected REST API (v1) with Swagger documentation.

## Features

- **Book management** — track titles, authors, genres, series, publishers, languages, formats, ISBN, page count, price, and read status
- **Cover images** — upload and display book covers
- **Manage entities** — CRUD interface for authors, genres, series, publishers, formats, and languages
- **Statistics** — view reading statistics and collection insights
- **REST API v1** — JSON endpoints for books, series, genres, languages, publishers, covers, export, and backups; protected with JWT authentication
- **Swagger UI** — interactive API documentation at `/api/docs`
- **Rate limiting** — configurable request limits via Flask-Limiter
- **Database migrations** — schema versioning with Alembic
- **Asset pipeline** — SASS and CoffeeScript compiled via Flask-Assets
- **Caching & compression** — Flask-Caching (file-system) and Flask-Compress

## Requirements

- Python 3.11
- [Pipenv](https://pipenv.pypa.io/)

## Quick Start

```bash
# Install dependencies
pip install pipenv
pipenv install

# Activate the virtual environment
pipenv shell

# Configure environment variables (copy and edit as needed)
cp .env.example .env   # or create .env manually — see Configuration below

# Run the development server
python -m flask --app librium:app run --debug
```

The application will be available at `http://127.0.0.1:5000`.

## Configuration

Librium uses environment variables loaded from a `.env` file (via python-dotenv). Key variables:

| Variable           | Default                    | Description                                                        |
|--------------------|----------------------------|--------------------------------------------------------------------|
| `APPLICATION_NAME` | `Librium`                  | Display name used in the UI                                        |
| `DATABASE_URL`     | `sqlite:///librium.sqlite` | SQLAlchemy database URI                                            |
| `FLASK_ENV`        | `development`              | Environment: `development`, `testing`, or `production`             |
| `JWT_SECRET_KEY`   | *(dev default)*            | Secret key for JWT token signing — **change in production**        |
| `SECRET_KEY`       | *(dev default)*            | Flask session secret — **change in production**                    |
| `DEFAULT_CURRENCY` | `USD`                      | Default currency for book prices                                   |
| `LOG_LEVEL`        | `INFO`                     | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)                |
| `LIBRIUM_CONFIG`   | *(auto)*                   | Override config class, e.g. `librium.core.config.ProductionConfig` |

Configuration classes are defined in `librium/core/config.py`:
- `DevelopmentConfig` — debug mode, verbose logging, asset debugging
- `TestingConfig` — in-memory SQLite, null cache, test JWT defaults
- `ProductionConfig` — debug off, secrets must be set via environment

## Project Structure

```
librium/
├── core/           # App factory, config, logging, assets, utils, rate limiting
├── database/
│   └── sqlalchemy/ # ORM models (Book, Author, Genre, Series, Publisher, Format, Language, etc.)
├── services/       # Business logic layer (one service per entity)
├── views/          # Flask blueprints
│   ├── main.py     # Home / statistics pages
│   ├── book.py     # Book browsing and detail views
│   ├── manage.py   # Entity CRUD management UI
│   ├── covers.py   # Cover image handling
│   ├── api/        # REST API blueprint
│   │   ├── v1/     # v1 endpoints and request schemas
│   │   └── swagger.py
│   └── views/      # Sub-views (authors, books, genres, series, years)
├── templates/      # Jinja2 templates
└── static/         # SASS, CoffeeScript, images, generated bundles
alembic/            # Database migration scripts
tests/              # Unit and integration tests
utils/              # Standalone utility scripts (export, etc.)
docs/               # Additional documentation
```

## API

The REST API lives under `/api/v1/` and requires a JWT bearer token. Obtain a token via:

```
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=<user>&password=<pass>
```

Key endpoints:

| Method | Path                     | Description                                  |
|--------|--------------------------|----------------------------------------------|
| GET    | `/api/v1/books`          | List books (paginated, filterable, sortable) |
| POST   | `/api/v1/add`            | Add a new book                               |
| POST   | `/api/v1/delete`         | Soft-delete a book                           |
| GET    | `/api/v1/series`         | List all series                              |
| GET    | `/api/v1/genres`         | List all genres                              |
| GET    | `/api/v1/languages`      | List all languages                           |
| GET    | `/api/v1/publishers`     | List all publishers                          |
| POST   | `/api/v1/export`         | Export collection to CSV                     |
| POST   | `/api/v1/backup/create`  | Create a database backup                     |
| GET    | `/api/v1/backup/list`    | List available backups                       |
| POST   | `/api/v1/backup/restore` | Restore from a backup                        |
| POST   | `/api/v1/backup/delete`  | Delete a backup                              |

Full interactive documentation is available at `/api/docs` (Swagger UI).

## Testing

```bash
# Run a specific test module
python -m unittest tests/test_models.py -v

# Run a specific test class or method
python -m unittest tests.test_models.TestBook -v
python -m unittest tests.test_models.TestBook.test_create_book -v

# Discover and run all tests
python -m unittest discover -s tests
```

Tests use in-memory SQLite by default when `FLASK_ENV=testing`. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on writing tests.

## Deployment

For production use with uWSGI:

```bash
uwsgi --ini uwsgi.ini
```

Adjust paths in `uwsgi.ini` to match your environment. Ensure `SECRET_KEY` and `JWT_SECRET_KEY` are set to strong, unique values.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding standards, and contribution workflow.

## License

MIT — see [LICENCE](LICENSE) for details.