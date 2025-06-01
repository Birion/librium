import os
import uuid
import atexit
from datetime import datetime
from decimal import Decimal
from typing import List

from dotenv import find_dotenv, load_dotenv
from pony.orm import *

# Import connection pool
from librium.database.pony.connection_pool import setup_connection_pool, close_all_pools

# Load environment and setup database
load_dotenv(find_dotenv())
db_file = os.getenv("SQLDATABASE")
db = Database(provider="sqlite", filename=db_file, create_db=True)

# Set up connection pooling
setup_connection_pool(db, db_file)

# Register a function to close all connection pools when the application exits
atexit.register(close_all_pools)

# Common constants
MAX_NAME_LENGTH = 50
MAX_AFFIX_LENGTH = 20
ISBN_LENGTH = 13
DEFAULT_INT_SIZE = 64


class Book(db.Entity):
    _table_ = "book"
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    isbn = Optional(str, ISBN_LENGTH)
    released = Optional(int, size=DEFAULT_INT_SIZE)
    page_count = Optional(
        int, size=DEFAULT_INT_SIZE, validator=lambda val: val is None or val > 0
    )
    price = Optional(Decimal, validator=lambda val: val is None or val >= 0)
    read = Required(bool, default=False)
    has_cover = Required(bool, default=False)

    def _validate_isbn(self, isbn):
        """Validate ISBN format."""
        if isbn is None:
            return True
        # Remove hyphens and spaces
        isbn = isbn.replace("-", "").replace(" ", "")
        # Check if ISBN is a valid ISBN-13
        if len(isbn) != 13 or not isbn.isdigit():
            return False
        # Check ISBN-13 checksum
        check_sum = sum(
            (3 if i % 2 else 1) * int(digit) for i, digit in enumerate(isbn[:12])
        )
        check_digit = (10 - (check_sum % 10)) % 10
        return int(isbn[12]) == check_digit

    def _validate_released(self, released):
        """Validate release year."""
        if released is None:
            return True
        current_year = datetime.now().year
        return (
            1000 <= released <= current_year + 5
        )  # Allow books up to 5 years in the future

    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))
    authors = Set("AuthorOrdering")
    publishers = Set("Publisher", table="book_publishers")
    format = Required("Format", default=1)
    languages = Set("Language", table="book_languages")
    genres = Set("Genre", table="book_genres")
    series = Set("SeriesIndex")

    @property
    def hex_uuid(self) -> str:
        return uuid.UUID(self.uuid).hex

    @property
    def name(self) -> str:
        return self.title

    @name.setter
    def name(self, value: str) -> None:
        self.title = value

    @property
    def ordered_authors(self) -> List["Author"]:
        return [a.author for a in self.authors.select().order_by(AuthorOrdering.idx)]

    @property
    def author_ids(self) -> List[int]:
        return [a.author.id for a in self.authors.select().order_by(AuthorOrdering.idx)]

    @property
    def genre_ids(self) -> List[int]:
        return [g.id for g in self.genres.select()]

    @property
    def publisher_ids(self) -> List[int]:
        return [p.id for p in self.publishers.select()]

    @property
    def language_ids(self) -> List[int]:
        return [l.id for l in self.languages.select()]

    @property
    def series_ids(self) -> List[int]:
        return [s.series.id for s in self.series.select()]


class Author(db.Entity):
    _table_ = "author"
    id = PrimaryKey(int, auto=True)
    first_name = Optional(str, MAX_NAME_LENGTH)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    middle_name = Optional(str, MAX_NAME_LENGTH)
    last_name = Optional(str, MAX_NAME_LENGTH)
    prefix = Optional(str, MAX_AFFIX_LENGTH)
    suffix = Optional(str, MAX_AFFIX_LENGTH)
    name = Optional(str)

    def _check_author_has_name(self):
        """Ensure that at least one name field is provided."""
        return bool(self.first_name or self.last_name or self.name)

    def _validate_name_length(self, attr, value):
        """Validate that name fields are not too long."""
        if value is None:
            return True
        max_length = (
            MAX_NAME_LENGTH
            if attr in ("first_name", "middle_name", "last_name")
            else None
        )
        if max_length and len(value) > max_length:
            return False
        return True

    def _validate_affix_length(self, attr, value):
        """Validate that prefix and suffix are not too long."""
        if value is None:
            return True
        max_length = MAX_AFFIX_LENGTH if attr in ("prefix", "suffix") else None
        if max_length and len(value) > max_length:
            return False
        return True

    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))
    books = Set("AuthorOrdering")

    @property
    def books_in_series(self):
        return select(b.book for b in self.books if not b.book.series.is_empty())

    @property
    def books_standalone(self):
        return select(b.book for b in self.books if b.book.series.is_empty())


class Publisher(db.Entity):
    _table_ = "publisher"
    id = PrimaryKey(int, auto=True)
    name = Required(
        str, 50, validator=lambda val: val and len(val.strip()) > 0 and len(val) <= 50
    )
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    def _validate_name(self, name):
        """Validate publisher name."""
        if not name or not name.strip():
            return False
        if len(name) > 50:
            return False
        return True

    books = Set(Book)


class Format(db.Entity):
    _table_ = "format"
    id = PrimaryKey(int, auto=True)
    name = Required(
        str, 50, validator=lambda val: val and len(val.strip()) > 0 and len(val) <= 50
    )
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    def _validate_name(self, name):
        """Validate format name."""
        if not name or not name.strip():
            return False
        if len(name) > 50:
            return False
        return True

    books = Set(Book)


class Language(db.Entity):
    _table_ = "language"
    id = PrimaryKey(int, auto=True)
    name = Required(
        str, 50, validator=lambda val: val and len(val.strip()) > 0 and len(val) <= 50
    )
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    def _validate_name(self, name):
        """Validate language name."""
        if not name or not name.strip():
            return False
        if len(name) > 50:
            return False
        return True

    books = Set(Book)


class Genre(db.Entity):
    _table_ = "genre"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    books = Set(Book)


class Series(db.Entity):
    _table_ = "series"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50, unique=True)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    books = Set("SeriesIndex")

    @property
    def has_unread_books(self) -> bool:
        return len(self.books.filter(lambda si: not si.book.read)) > 0

    @property
    def has_read_books(self) -> bool:
        return len(self.books.filter(lambda si: si.book.read)) > 0

    @property
    def books_read(self):
        return select(si for si in self.books if si.book.read)

    @property
    def books_unread(self):
        return select(si for si in self.books if not si.book.read)


class SeriesIndex(db.Entity):
    _table_ = "series_index"
    book = Required(Book)
    series = Required(Series)
    idx = Required(Decimal, default=0)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    PrimaryKey(book, series, idx)
    composite_index(book, idx)

    @property
    def index(self) -> Decimal:
        return int(self.idx) if not self.idx * 10 % 10 else self.idx


class AuthorOrdering(db.Entity):
    _table_ = "book_authors"
    book = Required(Book)
    author = Required(Author)
    idx = Required(int, default=0)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime)

    def before_update(self):
        """Update the updated_at timestamp before saving changes."""
        self.updated_at = datetime.now()

    PrimaryKey(book, author)
    composite_index(book, idx)


db.generate_mapping(create_tables=True)
