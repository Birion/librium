# Librium Database Schema

This document describes the current SQLAlchemy ORM schema used by Librium. It reflects the models defined in librium/database/sqlalchemy/db.py.

Notes
- All tables include soft-delete flags where relevant (deleted boolean) and timestamps where implemented (created_at, updated_at).
- UUID fields use string UUIDs (unique) for external references; integer primary keys are used for relations.
- Many-to-many relations are implemented with association tables.

Core Tables

1) book
- id: Integer, primary key
- title: String (unbounded in ORM, but subject to app-level validation)
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- isbn: String(13), nullable; both raw and hyphen/space-stripped forms are searched
- released: Integer, nullable (year), validated to [1000, current_year + 5]
- page_count: Integer, nullable
- price: Numeric(10, 2), nullable
- read: Boolean, default False
- has_cover: Boolean, default False
- uuid: String, unique, default UUID4
- deleted: Boolean, default False
- format_id: Integer, ForeignKey(format.id), not null

Relationships
- format: many-to-one to format (joined loading)
- authors: one-to-many to author_ordering (ordered authors for the book; cascade delete-orphan)
- publishers: many-to-many via book_publishers (joined loading)
- languages: many-to-many via book_languages (joined loading)
- genres: many-to-many via book_genres (joined loading)
- series: one-to-many to series_index (book placements in series; cascade delete-orphan)

Indexes
- Application-level indexes are defined on related tables; default sqlite pk index on id. Consider adding index on isbn for quicker lookup (some versions may already have this via Alembic migrations).

2) author
- id: Integer, primary key
- first_name: String(50), nullable
- middle_name: String(50), nullable
- last_name: String(50), nullable
- prefix: String(20), nullable
- suffix: String(20), nullable
- name: String (display/consolidated name)
- uuid: String, unique, default UUID4
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: one-to-many to author_ordering (links authors to books with an explicit order)

3) publisher
- id: Integer, primary key
- name: String(50), required
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: many-to-many with book via book_publishers

4) format
- id: Integer, primary key
- name: String(50), required, unique by convention
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: one-to-many from book (book.format_id)

5) language
- id: Integer, primary key
- name: String(50), required
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: many-to-many with book via book_languages

6) genre
- id: Integer, primary key
- name: String(50), required
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: many-to-many with book via book_genres

7) series
- id: Integer, primary key
- name: String(50), required
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- deleted: Boolean, default False

Relationships
- books: one-to-many via series_index (a series has multiple book placements)

8) series_index
Purpose: Associates a book with a series and records the book's index within that series.
- id: Integer, primary key
- series_id: Integer, ForeignKey(series.id)
- book_id: Integer, ForeignKey(book.id)
- idx: Integer (position of the book in the series)
- created_at: DateTime, default now
- updated_at: DateTime, nullable

Relationships
- series: many-to-one to series
- book: many-to-one to book

9) author_ordering
Purpose: Associates an author with a book and records the author's order for display.
- id: Integer, primary key
- author_id: Integer, ForeignKey(author.id)
- book_id: Integer, ForeignKey(book.id)
- idx: Integer (order of the author for the given book)
- created_at: DateTime, default now
- updated_at: DateTime, nullable

Relationships
- author: many-to-one to author
- book: many-to-one to book

10) authentication
Purpose: Stores credential records for API authentication.
- id: Integer, primary key
- username: String, unique
- password_hash: String (hashed)
- created_at: DateTime, default now
- updated_at: DateTime, nullable
- active: Boolean, default True
- uuid: String, unique, default UUID4

Association Tables

A) book_publishers
- book_id: Integer, ForeignKey(book.id), primary key
- publisher_id: Integer, ForeignKey(publisher.id), primary key

B) book_languages
- book_id: Integer, ForeignKey(book.id), primary key
- language_id: Integer, ForeignKey(language.id), primary key

C) book_genres
- book_id: Integer, ForeignKey(book.id), primary key
- genre_id: Integer, ForeignKey(genre.id), primary key

Validation and Business Rules (high level)
- Book.validate_isbn: ensures ISBN length/characters; supports hyphen/space normalization.
- Book.validate_released: bounds check for plausible year range.
- Author.validate_name_length / validate_affix_length: enforce length limits.
- Publisher/Format/Language name validation: non-empty, max length 50.
- Series and related classes include created_at/updated_at and soft-delete (where applicable) and support querying helpers.

Engine and Sessions
- SQLite engine is created from the SQLDATABASE environment variable (legacy), with QueuePool and pooling parameters set; tests may override engine or set SQLDATABASE=":memory:".
- Session is provided via scoped_session(Session).

Indices
- Explicit Index objects may be added via migrations; primary keys are indexed by default. Consider indexing frequently queried columns such as book.isbn, author.name.

This document should be kept in sync with db.py and Alembic migrations.