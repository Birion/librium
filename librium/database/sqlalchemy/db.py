"""
SQLAlchemy database models for the Librium application.

This module defines the SQLAlchemy models for the Librium application,
replacing the Pony ORM models.
"""

import atexit
import os
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    create_engine,
    event,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)
from sqlalchemy.pool import QueuePool
from typing_extensions import Annotated

# Common constants
MAX_NAME_LENGTH = 50
MAX_AFFIX_LENGTH = 20
ISBN_LENGTH = 13
DEFAULT_INT_SIZE = 64

# Load environment and setup database
load_dotenv(find_dotenv())
db_file = os.getenv("SQLDATABASE")
engine = create_engine(
    f"sqlite:///{db_file}",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True,
)

# Create a session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
str_name = Annotated[str, mapped_column(String)]
str_uuid = Annotated[
    str, mapped_column(String, unique=True, default=lambda: str(uuid.uuid4()))
]

str_max = Annotated[str, Column(String(MAX_NAME_LENGTH))]
str_max_affix = Annotated[str, Column(String(MAX_AFFIX_LENGTH))]
str_max_isbn = Annotated[str, Column(String(ISBN_LENGTH))]

int_max = Annotated[int, Column(Integer)]
int_max_size = Annotated[int, Column(Integer, default=DEFAULT_INT_SIZE)]
int_max_size_nullable = Annotated[
    Optional[int], Column(Integer, default=None, nullable=True)
]
int_max_size_unique = Annotated[
    int, Column(Integer, default=DEFAULT_INT_SIZE, unique=True)
]
int_max_size_nullable_unique = Annotated[
    Optional[int], Column(Integer, default=None, nullable=True, unique=True)
]
bool_default_true = Annotated[bool, Column(Boolean, default=True)]
bool_default_false = Annotated[bool, Column(Boolean, default=False)]


# Create a base class for declarative models
class Base(DeclarativeBase):
    pass


# Association tables for many-to-many relationships
book_publishers = Table(
    "book_publishers",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("publisher_id", Integer, ForeignKey("publisher.id"), primary_key=True),
)

book_languages = Table(
    "book_languages",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("language_id", Integer, ForeignKey("language.id"), primary_key=True),
)

book_genres = Table(
    "book_genres",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genre.id"), primary_key=True),
)


class Book(Base):
    """Book model representing a book in the library."""

    __tablename__ = "book"

    id: Mapped[int_pk]
    title: Mapped[str_name]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    isbn: Mapped[Optional[str_max_isbn]]
    released: Mapped[Optional[int]]
    page_count: Mapped[Optional[int]]
    price: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2))
    read: Mapped[bool] = mapped_column(default=False)
    has_cover: Mapped[bool] = mapped_column(default=False)
    uuid: Mapped[str_uuid]

    # Relationships
    format_id: Mapped[int] = mapped_column(ForeignKey("format.id"))
    format: Mapped["Format"] = relationship(back_populates="books", lazy="joined")

    authors: Mapped[List["AuthorOrdering"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", lazy="joined"
    )
    publishers: Mapped[List["Publisher"]] = relationship(
        secondary=book_publishers, back_populates="books", lazy="joined"
    )
    languages: Mapped[List["Language"]] = relationship(
        secondary=book_languages, back_populates="books", lazy="joined"
    )
    genres: Mapped[List["Genre"]] = relationship(
        secondary=book_genres, back_populates="books", lazy="joined"
    )
    series: Mapped[List["SeriesIndex"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", lazy="joined"
    )

    def set(self, **kwargs):
        """Set multiple attributes at once."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def create(cls, **kwargs):
        """Create a new book."""
        book = cls(**kwargs)
        book.set(uuid=str(uuid.uuid4()))

    @property
    def hex_uuid(self) -> str:
        """Return the UUID as a hex string."""
        return uuid.UUID(self.uuid).hex

    @property
    def name(self) -> str:
        """Return the book title."""
        return self.title

    @name.setter
    def name(self, value: str) -> None:
        """Set the book title."""
        self.title = value

    @property
    def ordered_authors(self) -> List["Author"]:
        """Return the authors ordered by their index."""
        return [a.author for a in sorted(self.authors, key=lambda x: x.idx)]

    @property
    def author_ids(self) -> List[int]:
        """Return the IDs of the authors ordered by their index."""
        return [a.author.id for a in sorted(self.authors, key=lambda x: x.idx)]

    @property
    def genre_ids(self) -> List[int]:
        """Return the IDs of the genres."""
        return [g.id for g in self.genres]

    @property
    def publisher_ids(self) -> List[int]:
        """Return the IDs of the publishers."""
        return [p.id for p in self.publishers]

    @property
    def language_ids(self) -> List[int]:
        """Return the IDs of the languages."""
        return [l.id for l in self.languages]

    @property
    def series_ids(self) -> List[int]:
        """Return the IDs of the series."""
        return [s.series.id for s in self.series]

    @staticmethod
    def _validate_isbn(isbn):
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

    @staticmethod
    def _validate_released(released):
        """Validate release year."""
        if released is None:
            return True
        current_year = datetime.now().year
        return (
            1000 <= released <= current_year + 5
        )  # Allow books up to 5 years in the future

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"


class Author(Base):
    """Author model representing a book author."""

    __tablename__ = "author"

    id: Mapped[int_pk]
    first_name: Mapped[Optional[str_max]]
    middle_name: Mapped[Optional[str_max]]
    last_name: Mapped[Optional[str_max]]
    prefix: Mapped[Optional[str_max_affix]]
    suffix: Mapped[Optional[str_max_affix]]
    name: Mapped[str] = mapped_column(String)
    uuid: Mapped[str_uuid]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["AuthorOrdering"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def _check_author_has_name(self):
        """Ensure that at least one name field is provided."""
        return bool(self.first_name or self.last_name or self.name)

    @staticmethod
    def _validate_name_length(attr, value):
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

    @staticmethod
    def _validate_affix_length(attr, value):
        """Validate that prefix and suffix are not too long."""
        if value is None:
            return True
        max_length = MAX_AFFIX_LENGTH if attr in ("prefix", "suffix") else None
        if max_length and len(value) > max_length:
            return False
        return True

    @property
    def books_in_series(self):
        """Return books by this author that are part of a series."""
        return [b.book for b in self.books if b.book.series]

    @property
    def books_standalone(self):
        """Return books by this author that are not part of a series."""
        return [b.book for b in self.books if not b.book.series]

    def __repr__(self):
        if self.name:
            return f"<Author(id={self.id}, name='{self.name}')>"
        else:
            return f"<Author(id={self.id}, name='{self.first_name} {self.last_name}')>"


class Publisher(Base):
    """Publisher model representing a book publisher."""

    __tablename__ = "publisher"

    id: Mapped[int_pk]
    name: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        secondary=book_publishers, back_populates="publishers"
    )

    @staticmethod
    def _validate_name(name):
        """Validate publisher name."""
        if not name or not name.strip():
            return False
        if len(name) > MAX_NAME_LENGTH:
            return False
        return True

    def __repr__(self):
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Format(Base):
    """Format model representing a book format (e.g., hardcover, paperback)."""

    __tablename__ = "format"

    id: Mapped[int_pk]
    name: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["Book"]] = relationship(back_populates="format")

    @staticmethod
    def _validate_name(name):
        """Validate format name."""
        if not name or not name.strip():
            return False
        if len(name) > MAX_NAME_LENGTH:
            return False
        return True

    def __repr__(self):
        return f"<Format(id={self.id}, name='{self.name}')>"


class Language(Base):
    """Language model representing a book language."""

    __tablename__ = "language"

    id: Mapped[int_pk]
    name: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        secondary=book_languages, back_populates="languages"
    )

    @staticmethod
    def _validate_name(name):
        """Validate language name."""
        if not name or not name.strip():
            return False
        if len(name) > MAX_NAME_LENGTH:
            return False
        return True

    def __repr__(self):
        return f"<Language(id={self.id}, name='{self.name}')>"


class Genre(Base):
    """Genre model representing a book genre."""

    __tablename__ = "genre"

    id: Mapped[int_pk]
    name: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        secondary=book_genres, back_populates="genres"
    )

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Series(Base):
    """Series model representing a book series."""

    __tablename__ = "series"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(
        String(MAX_NAME_LENGTH), nullable=False, unique=True
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    books: Mapped[List["SeriesIndex"]] = relationship(
        back_populates="series", cascade="all, delete-orphan"
    )

    @property
    def has_unread_books(self) -> bool:
        """Return whether the series has any unread books."""
        return any(not si.book.read for si in self.books)

    @property
    def has_read_books(self) -> bool:
        """Return whether the series has any read books."""
        return any(si.book.read for si in self.books)

    @property
    def books_read(self):
        """Return the read books in the series."""
        return [si for si in self.books if si.book.read]

    @property
    def books_unread(self):
        """Return the unread books in the series."""
        return [si for si in self.books if not si.book.read]

    def __repr__(self):
        return f"<Series(id={self.id}, name='{self.name}')>"


class SeriesIndex(Base):
    """SeriesIndex model representing a book's position in a series."""

    __tablename__ = "series_index"

    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("book.id"), primary_key=True
    )
    series_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("series.id"), primary_key=True
    )
    idx: Mapped[Decimal] = mapped_column(Numeric, primary_key=True, default=0)

    # Relationships
    book: Mapped["Book"] = relationship(back_populates="series")
    series: Mapped["Series"] = relationship(back_populates="books")

    @property
    def index(self) -> Decimal:
        """Return the index as an integer if it's a whole number, otherwise as a decimal."""
        return int(self.idx) if not self.idx * 10 % 10 else self.idx

    def __repr__(self):
        return f"<SeriesIndex(book_id={self.book_id}, series_id={self.series_id}, idx={self.idx})>"


class AuthorOrdering(Base):
    """AuthorOrdering model representing the order of authors for a book."""

    __tablename__ = "book_authors"

    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("book.id"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("author.id"), primary_key=True
    )
    idx: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    book: Mapped["Book"] = relationship(back_populates="authors")
    author: Mapped["Author"] = relationship(back_populates="books")

    def __repr__(self):
        return f"<AuthorOrdering(book_id={self.book_id}, author_id={self.author_id}, idx={self.idx})>"


# Create indexes for frequently queried fields
Index("idx_book_title", Book.title)
Index("idx_book_read", Book.read)
Index("idx_book_uuid", Book.uuid)
Index("idx_author_last_name", Author.last_name)
Index("idx_series_name", Series.name)
Index("idx_book_authors_idx", AuthorOrdering.book_id, AuthorOrdering.idx)
Index("idx_series_index_idx", SeriesIndex.book_id, SeriesIndex.idx)


# Event listeners for updating timestamps
@event.listens_for(Book, "before_update")
def book_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Author, "before_update")
def author_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Publisher, "before_update")
def publisher_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Format, "before_update")
def format_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Language, "before_update")
def language_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Genre, "before_update")
def genre_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Series, "before_update")
def series_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(SeriesIndex, "before_update")
def series_index_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(AuthorOrdering, "before_update")
def author_ordering_before_update(mapper, connection, target):
    target.updated_at = datetime.now()


# Create all tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(engine)


# Drop all tables
def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(engine)


# Initialize the database
def init_db():
    """Initialize the database."""
    create_tables()


# Close the connection pool when the application exits
@atexit.register
def close_connection_pool():
    """Close the connection pool when the application exits."""
    engine.dispose()
