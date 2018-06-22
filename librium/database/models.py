import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

from librium.database.db import Base


@generic_repr
class Format(Base):
    __tablename__ = "format"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="format")


@generic_repr
class Language(Base):
    __tablename__ = "language"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="language")


@generic_repr
class Genre(Base):
    __tablename__ = "genre"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="genres", secondary="book_genres")


@generic_repr
class Series(Base):
    __tablename__ = "series"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="series", secondary="series_index")


@generic_repr
class Book(Base):
    __tablename__ = "book"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))
    price = sa.Column(sa.Integer)
    page_count = sa.Column(sa.Integer, nullable=True)
    isbn = sa.Column(sa.String(13), unique=True)
    read = sa.Column(sa.Boolean, default=False, nullable=False)
    uuid = sa.Column(sau.UUIDType, unique=True)

    authors = relationship("Author", back_populates="books", secondary="book_authors")
    publishers = relationship(
        "Publisher", back_populates="books", secondary="book_publishers"
    )
    genres = relationship("Genre", back_populates="books", secondary="book_genres")
    series = relationship("Series", back_populates="books", secondary="series_index")

    format_id = sa.Column(sa.Integer, sa.ForeignKey("format.id"))
    format = relationship("Format", back_populates="books", primaryjoin=format_id == Format.id)
    language_id = sa.Column(sa.Integer, sa.ForeignKey("language.id"))
    language = relationship("Language", back_populates="books", primaryjoin=language_id == Language.id)


@generic_repr
class Author(Base):
    __tablename__ = "author"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(50))
    last_name = sa.Column(sa.String(50))
    middle_name = sa.Column(sa.String(50), nullable=True, default=None)
    prefix = sa.Column(sa.String(20), nullable=True, default=None)
    suffix = sa.Column(sa.String(20), nullable=True, default=None)
    uuid = sa.Column(sau.UUIDType, unique=True)

    sa.UniqueConstraint("prefix", "first_name", "middle_name", "last_name", "suffix", name="unique_author")

    books = relationship("Book", back_populates="authors", secondary="book_authors")


@generic_repr
class Publisher(Base):
    __tablename__ = "publisher"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="publishers", secondary="book_publishers")


@generic_repr
class SeriesIndex(Base):
    __tablename__ = "series_index"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey("series.id"), primary_key=True)

    idx = sa.Column(sa.Float, sa.CheckConstraint("idx>=0", name="positive_index"))


book_authors = sa.Table(
    "book_authors",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("author_id", sa.ForeignKey("author.id"), primary_key=True),
)

book_publishers = sa.Table(
    "book_publishers",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("publisher_id", sa.ForeignKey("publisher.id"), primary_key=True),
)

book_genres = sa.Table(
    "book_genres",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("genre_id", sa.ForeignKey("genre.id"), primary_key=True),
)
