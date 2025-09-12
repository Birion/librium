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
    # echo=True,
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
    deleted: Mapped[bool] = mapped_column(default=False)

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

    @classmethod
    def find_by_isbn(cls, session, isbn: Optional[str], include_deleted: bool = False):
        """Find a single book by ISBN.

        - Normalizes the input by removing hyphens and spaces.
        - Respects soft-delete flag by default.
        """
        if not isbn:
            return None
        normalized = isbn.replace("-", "").replace(" ", "")
        q = session.query(cls).filter(cls.isbn.in_([isbn, normalized]))
        if not include_deleted:
            q = q.filter(cls.deleted.is_(False))
        return q.first()

    @classmethod
    def search_by_title(
        cls,
        session,
        query: Optional[str],
        include_deleted: bool = False,
        limit: Optional[int] = None,
    ) -> List["Book"]:
        """Case-insensitive substring search by title.

        Returns a list of books matching the query. By default excludes soft-deleted
        records. You can pass limit to cap the number of results.
        """
        if not query:
            return []
        q = session.query(cls).filter(cls.title.ilike(f"%{query}%"))
        if not include_deleted:
            q = q.filter(cls.deleted.is_(False))
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    @staticmethod
    def validate_isbn(isbn):
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
    def validate_released(released):
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
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    books: Mapped[List["AuthorOrdering"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def check_author_has_name(self):
        """Ensure that at least one name field is provided."""
        return bool(self.first_name or self.last_name or self.name)

    @staticmethod
    def validate_name_length(attr, value):
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
    def validate_affix_length(attr, value):
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

    @classmethod
    def find_by_name(
        cls,
        session,
        name: Optional[str],
        include_deleted: bool = False,
        limit: Optional[int] = None,
    ) -> List["Author"]:
        """Find authors by their display name (case-insensitive, substring).

        Uses the consolidated `name` column. Returns an empty list on falsy input.
        """
        if not name:
            return []
        q = session.query(cls).filter(cls.name.ilike(f"%{name}%"))
        if not include_deleted:
            q = q.filter(cls.deleted.is_(False))
        if limit is not None:
            q = q.limit(limit)
        return q.all()

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
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        secondary=book_publishers, back_populates="publishers"
    )

    @staticmethod
    def validate_name(name):
        """Validate publisher name."""
        if not name or not name.strip():
            return False
        if len(name) > MAX_NAME_LENGTH:
            return False
        return True

    @classmethod
    def find_by_name(
        cls,
        session,
        name: Optional[str],
        include_deleted: bool = False,
        limit: Optional[int] = None,
    ) -> List["Publisher"]:
        """Find publishers by name (case-insensitive, substring)."""
        if not name:
            return []
        q = session.query(cls).filter(cls.name.ilike(f"%{name}%"))
        if not include_deleted:
            q = q.filter(cls.deleted.is_(False))
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def __repr__(self):
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Format(Base):
    """Format model representing a book format (e.g., hardcover, paperback)."""

    __tablename__ = "format"

    id: Mapped[int_pk]
    name: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    books: Mapped[List["Book"]] = relationship(back_populates="format")

    @staticmethod
    def validate_name(name):
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
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        secondary=book_languages, back_populates="languages"
    )

    @staticmethod
    def validate_name(name):
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
    deleted: Mapped[bool] = mapped_column(default=False)

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
    deleted: Mapped[bool] = mapped_column(default=False)

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

    @classmethod
    def find_by_name(
        cls,
        session,
        name: Optional[str],
        include_deleted: bool = False,
        limit: Optional[int] = None,
    ) -> List["Series"]:
        """Find series by name (case-insensitive, substring)."""
        if not name:
            return []
        q = session.query(cls).filter(cls.name.ilike(f"%{name}%"))
        if not include_deleted:
            q = q.filter(cls.deleted.is_(False))
        if limit is not None:
            q = q.limit(limit)
        return q.all()

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


class Authentication(Base):
    """Authentication model for user authentication."""

    __tablename__ = "authentication"

    id: Mapped[int_pk]
    username: Mapped[str_max] = mapped_column(String, unique=True)
    password_hash: Mapped[str_max]
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    deleted: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"<Authentication(id={self.id}, username='{self.username}')>"

    def set_password(self, password: str):
        """Set the password hash for the user."""
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)


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
    validate_book(target)


@event.listens_for(Book, "before_insert")
def book_before_insert(mapper, connection, target):
    validate_book(target)


@event.listens_for(Author, "before_update")
def author_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_author(target)


@event.listens_for(Author, "before_insert")
def author_before_insert(mapper, connection, target):
    validate_author(target)


@event.listens_for(Publisher, "before_update")
def publisher_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_publisher(target)


@event.listens_for(Publisher, "before_insert")
def publisher_before_insert(mapper, connection, target):
    validate_publisher(target)


@event.listens_for(Format, "before_update")
def format_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_format(target)


@event.listens_for(Format, "before_insert")
def format_before_insert(mapper, connection, target):
    validate_format(target)


@event.listens_for(Language, "before_update")
def language_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_language(target)


@event.listens_for(Language, "before_insert")
def language_before_insert(mapper, connection, target):
    validate_language(target)


@event.listens_for(Genre, "before_update")
def genre_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_genre(target)


@event.listens_for(Genre, "before_insert")
def genre_before_insert(mapper, connection, target):
    validate_genre(target)


@event.listens_for(Series, "before_update")
def series_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
    validate_series(target)


@event.listens_for(Series, "before_insert")
def series_before_insert(mapper, connection, target):
    validate_series(target)


@event.listens_for(SeriesIndex, "before_update")
def series_index_before_update(mapper, connection, target):
    validate_series_index(target)


@event.listens_for(SeriesIndex, "before_insert")
def series_index_before_insert(mapper, connection, target):
    validate_series_index(target)


@event.listens_for(AuthorOrdering, "before_update")
def author_ordering_before_update(mapper, connection, target):
    validate_author_ordering(target)


@event.listens_for(AuthorOrdering, "before_insert")
def author_ordering_before_insert(mapper, connection, target):
    validate_author_ordering(target)


# Validation functions
def validate_book(book):
    """Validate book data before insert or update."""
    # Validate title
    if not book.title or not book.title.strip():
        raise ValueError("Book title cannot be empty")

    # Validate ISBN
    if book.isbn and not Book.validate_isbn(book.isbn):
        raise ValueError(f"Invalid ISBN format: {book.isbn}")

    # Validate release year
    if book.released is not None and not Book.validate_released(book.released):
        raise ValueError(f"Invalid release year: {book.released}")

    # Validate page count
    if book.page_count is not None and book.page_count <= 0:
        raise ValueError(f"Page count must be positive: {book.page_count}")

    # Validate price
    if book.price is not None and book.price < 0:
        raise ValueError(f"Price cannot be negative: {book.price}")


def validate_author(author):
    """Validate author data before insert or update."""
    # Ensure author has at least one name field
    if not author.check_author_has_name():
        raise ValueError("Author must have at least one name field")

    # Validate name lengths
    for attr in ["first_name", "middle_name", "last_name"]:
        value = getattr(author, attr)
        if value and not Author.validate_name_length(attr, value):
            raise ValueError(f"Author {attr} is too long: {value}")

    # Validate affix lengths
    for attr in ["prefix", "suffix"]:
        value = getattr(author, attr)
        if value and not Author.validate_affix_length(attr, value):
            raise ValueError(f"Author {attr} is too long: {value}")


def validate_publisher(publisher):
    """Validate publisher data before insert or update."""
    if not Publisher.validate_name(publisher.name):
        raise ValueError(f"Invalid publisher name: {publisher.name}")


def validate_format(format):
    """Validate format data before insert or update."""
    if not Format.validate_name(format.name):
        raise ValueError(f"Invalid format name: {format.name}")


def validate_language(language):
    """Validate language data before insert or update."""
    if not Language.validate_name(language.name):
        raise ValueError(f"Invalid language name: {language.name}")


def validate_genre(genre):
    """Validate genre data before insert or update."""
    if not genre.name or not genre.name.strip():
        raise ValueError("Genre name cannot be empty")
    if len(genre.name) > MAX_NAME_LENGTH:
        raise ValueError(f"Genre name is too long: {genre.name}")


def validate_series(series):
    """Validate series data before insert or update."""
    if not series.name or not series.name.strip():
        raise ValueError("Series name cannot be empty")
    if len(series.name) > MAX_NAME_LENGTH:
        raise ValueError(f"Series name is too long: {series.name}")


def validate_series_index(series_index):
    """Validate series index data before insert or update."""
    if series_index.idx < 0:
        raise ValueError(f"Series index cannot be negative: {series_index.idx}")


def validate_author_ordering(author_ordering):
    """Validate author ordering data before insert or update."""
    if author_ordering.idx < 0:
        raise ValueError(
            f"Author ordering index cannot be negative: {author_ordering.idx}"
        )


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
