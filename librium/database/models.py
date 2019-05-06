import uuid

import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.collections import InstrumentedList
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

    books = relationship("Book", back_populates="languages", secondary="book_languages")


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
    name = sa.Column(sa.String(50), unique=True)

    books = relationship("SeriesIndex", back_populates="series")


@generic_repr
class Book(Base):
    __tablename__ = "book"
    RELATIONSHIPS_TO_DICT = True

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(250))
    isbn = sa.Column(sa.String(13))
    released = sa.Column(sa.Integer)
    page_count = sa.Column(sa.Integer, nullable=True)
    price = sa.Column(sa.Float)
    read = sa.Column(sa.Boolean(name="read_bool"), default=False, nullable=False)
    has_cover = sa.Column(sa.Boolean(name="cover_bool"), default=False, nullable=False)
    uuid = sa.Column(sau.UUIDType, unique=True, default=uuid.uuid4)

    authors = relationship(
        "Author",
        back_populates="books",
        secondary="book_authors",
        cascade="all, delete",
    )
    publishers = relationship(
        "Publisher",
        back_populates="books",
        secondary="book_publishers",
        cascade="all, delete",
    )
    genres = relationship(
        "Genre", back_populates="books", secondary="book_genres", cascade="all, delete"
    )
    series = relationship("SeriesIndex", back_populates="book", cascade="all, delete")
    languages = relationship(
        "Language",
        back_populates="books",
        secondary="book_languages",
        cascade="all, delete",
    )

    format_id = sa.Column(sa.Integer, sa.ForeignKey("format.id"))
    format = relationship(
        "Format", back_populates="books", primaryjoin=format_id == Format.id
    )

    @staticmethod
    def add(rel: InstrumentedList, table: Base, value: dict):
        try:
            item = table.query.filter_by(**value).one()
        except NoResultFound:
            item = table(**value)
        rel.append(item)

    @staticmethod
    def remove(rel: InstrumentedList, table: Base, value: dict):
        try:
            item = table.query.filter_by(**value).one()
            rel.remove(item)
        except NoResultFound:
            pass

    @property
    def price_(self):
        if self.price * 10 % 10:
            return self.price
        else:
            return int(self.price)


def make_author_name(context) -> str:
    parameters = context.get_current_parameters()
    order = [parameters["prefix"], parameters["first_name"], parameters["middle_name"], parameters["last_name"], parameters["suffix"]]
    return " ".join(x for x in order if x)


@generic_repr
class Author(Base):
    __tablename__ = "author"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(50))
    middle_name = sa.Column(sa.String(50), nullable=True, default=None)
    last_name = sa.Column(sa.String(50))
    prefix = sa.Column(sa.String(20), nullable=True, default=None)
    suffix = sa.Column(sa.String(20), nullable=True, default=None)
    name = sa.Column(sa.String, default=make_author_name)
    uuid = sa.Column(sau.UUIDType, unique=True, default=uuid.uuid4)

    books = relationship("Book", back_populates="authors", secondary="book_authors")


@generic_repr
class Publisher(Base):
    __tablename__ = "publisher"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship(
        "Book", back_populates="publishers", secondary="book_publishers"
    )


@generic_repr
class SeriesIndex(Base):
    __tablename__ = "series_index"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey("series.id"), primary_key=True)

    book = relationship("Book", back_populates="series")
    series = relationship("Series", back_populates="books")

    idx = sa.Column(
        sa.Float, primary_key=True, default=0
    )

    sa.CheckConstraint("idx>=0", name="positive_index")


class BookAuthors(Base):
    __tablename__ = "book_authors"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("author.id"), primary_key=True)


class BookPublishers(Base):
    __tablename__ = "book_publishers"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    publisher_id = sa.Column(sa.Integer, sa.ForeignKey("publisher.id"), primary_key=True)


class BookGenres(Base):
    __tablename__ = "book_genres"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey("genre.id"), primary_key=True)


class BookLanguages(Base):
    __tablename__ = "book_languages"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book.id"), primary_key=True)
    language_id = sa.Column(sa.Integer, sa.ForeignKey("language.id"), primary_key=True)
