# Database Schema

Librium uses SQLAlchemy ORM with SQLite as the default database. Models are defined in `librium/database/sqlalchemy/db.py`.

## Entity-Relationship Overview

```
Book ──┬── many-to-many ── Author      (via book_author + AuthorOrdering)
       ├── many-to-many ── Genre       (via book_genre)
       ├── many-to-many ── Publisher   (via book_publisher)
       ├── many-to-many ── Language    (via book_language)
       ├── one-to-many  ── SeriesIndex (Book → SeriesIndex → Series)
       └── many-to-one  ── Format
```

## Models

### Book

The central entity representing a book in the library.

| Column       | Type         | Description                           |
|--------------|--------------|---------------------------------------|
| `id`         | Integer (PK) | Auto-increment primary key            |
| `uuid`       | String(32)   | Unique identifier (hex UUID)          |
| `title`      | String       | Book title                            |
| `isbn`       | String       | ISBN (validated format)               |
| `released`   | Integer      | Year of publication                   |
| `price`      | Numeric      | Purchase price                        |
| `page_count` | Integer      | Number of pages                       |
| `read`       | Boolean      | Read status                           |
| `has_cover`  | Boolean      | Whether a cover image exists          |
| `format_id`  | Integer (FK) | Reference to Format                   |
| `created_at` | DateTime     | Auto-set on creation                  |
| `updated_at` | DateTime     | Auto-set on update                    |
| `deleted_at` | DateTime     | Soft-delete timestamp (null = active) |

**Relationships:** `authors` (via AuthorOrdering), `genres`, `publishers`, `languages`, `series` (via SeriesIndex), `format`

**Class methods:** `find_by_isbn()`, `search_by_title()`

**Validators:** `validate_isbn()`, `validate_released()`

### Author

| Column       | Type         | Description                |
|--------------|--------------|----------------------------|
| `id`         | Integer (PK) | Auto-increment primary key |
| `name`       | String       | Display name               |
| `first_name` | String       | First name                 |
| `last_name`  | String       | Last name                  |
| `prefix`     | String       | Name prefix (e.g. "Dr.")   |
| `suffix`     | String       | Name suffix (e.g. "Jr.")   |
| `created_at` | DateTime     | Auto-set on creation       |
| `updated_at` | DateTime     | Auto-set on update         |
| `deleted_at` | DateTime     | Soft-delete timestamp      |

**Validators:** `check_author_has_name()`, `validate_name_length()`, `validate_affix_length()`

**Properties:** `books_in_series`, `books_standalone`

### Genre

| Column       | Type         | Description                |
|--------------|--------------|----------------------------|
| `id`         | Integer (PK) | Auto-increment primary key |
| `name`       | String       | Genre name                 |
| `created_at` | DateTime     | Auto-set on creation       |
| `updated_at` | DateTime     | Auto-set on update         |
| `deleted_at` | DateTime     | Soft-delete timestamp      |

### Series

| Column       | Type         | Description                |
|--------------|--------------|----------------------------|
| `id`         | Integer (PK) | Auto-increment primary key |
| `name`       | String       | Series name                |
| `created_at` | DateTime     | Auto-set on creation       |
| `updated_at` | DateTime     | Auto-set on update         |
| `deleted_at` | DateTime     | Soft-delete timestamp      |

**Properties:** `has_unread_books`, `has_read_books`, `books_read`, `books_unread`

### SeriesIndex

Junction table linking books to series with an ordering index.

| Column         | Type         | Description                        |
|----------------|--------------|------------------------------------|
| `id`           | Integer (PK) | Auto-increment primary key         |
| `book_id`      | Integer (FK) | Reference to Book                  |
| `series_id`    | Integer (FK) | Reference to Series                |
| `series_index` | Float        | Position of the book in the series |

### Publisher

| Column       | Type         | Description                |
|--------------|--------------|----------------------------|
| `id`         | Integer (PK) | Auto-increment primary key |
| `name`       | String       | Publisher name (validated) |
| `created_at` | DateTime     | Auto-set on creation       |
| `updated_at` | DateTime     | Auto-set on update         |
| `deleted_at` | DateTime     | Soft-delete timestamp      |

### Format

| Column       | Type         | Description                             |
|--------------|--------------|-----------------------------------------|
| `id`         | Integer (PK) | Auto-increment primary key              |
| `name`       | String       | Format name (e.g. Hardcover, Paperback) |
| `created_at` | DateTime     | Auto-set on creation                    |
| `updated_at` | DateTime     | Auto-set on update                      |
| `deleted_at` | DateTime     | Soft-delete timestamp                   |

### Language

| Column       | Type         | Description                |
|--------------|--------------|----------------------------|
| `id`         | Integer (PK) | Auto-increment primary key |
| `name`       | String       | Language name (validated)  |
| `created_at` | DateTime     | Auto-set on creation       |
| `updated_at` | DateTime     | Auto-set on update         |
| `deleted_at` | DateTime     | Soft-delete timestamp      |

### AuthorOrdering

Junction table linking books to authors with display ordering.

| Column      | Type         | Description                              |
|-------------|--------------|------------------------------------------|
| `id`        | Integer (PK) | Auto-increment primary key               |
| `book_id`   | Integer (FK) | Reference to Book                        |
| `author_id` | Integer (FK) | Reference to Author                      |
| `ordering`  | Integer      | Display order of the author for the book |

### Authentication

| Column          | Type         | Description                |
|-----------------|--------------|----------------------------|
| `id`            | Integer (PK) | Auto-increment primary key |
| `username`      | String       | Unique username            |
| `password_hash` | String       | Bcrypt-hashed password     |
| `created_at`    | DateTime     | Auto-set on creation       |
| `updated_at`    | DateTime     | Auto-set on update         |

**Methods:** `set_password()`, `check_password()`

## Association Tables

| Table            | Links            | Purpose                                    |
|------------------|------------------|--------------------------------------------|
| `book_author`    | Book ↔ Author    | Many-to-many (ordering via AuthorOrdering) |
| `book_genre`     | Book ↔ Genre     | Many-to-many                               |
| `book_publisher` | Book ↔ Publisher | Many-to-many                               |
| `book_language`  | Book ↔ Language  | Many-to-many                               |

## Common Patterns

- **Soft delete:** All main entities have a `deleted_at` column. Queries should filter `deleted_at IS NULL` for active records (services handle this automatically).
- **Timestamps:** `created_at` and `updated_at` are managed by SQLAlchemy event listeners (`before_insert`, `before_update`).
- **Validation:** Models use `@validates` decorators and standalone `validate_*` functions called from event listeners.

## Migrations

Schema changes are managed with Alembic. Migration scripts live in `alembic/versions/`.

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "description of change"

# Apply migrations
alembic upgrade head

# Check current revision
alembic current
```
