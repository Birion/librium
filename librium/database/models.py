import uuid

import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

from librium.database.db import Base, db_session
from librium.database.mixin import OutputMixin


@generic_repr
class Format(OutputMixin, Base):
    __tablename__ = "format"

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="format")


@generic_repr
class Language(OutputMixin, Base):
    __tablename__ = "language"

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="languages", secondary="book_languages")


@generic_repr
class Genre(OutputMixin, Base):
    __tablename__ = "genre"

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship("Book", back_populates="genres", secondary="book_genres")


@generic_repr
class Series(OutputMixin, Base):
    __tablename__ = "series"

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), unique=True)

    books = relationship("SeriesIndex", back_populates="series")


@generic_repr
class Book(OutputMixin, Base):
    __tablename__ = "book"
    RELATIONSHIPS_TO_DICT = True

    _id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(250))
    price = sa.Column(sa.Integer)
    page_count = sa.Column(sa.Integer, nullable=True)
    isbn = sa.Column(sa.String(13))
    read = sa.Column(sa.Boolean, default=False, nullable=False)
    _uuid = sa.Column(sau.UUIDType, unique=True)

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

    format_id = sa.Column(sa.Integer, sa.ForeignKey("format._id"))
    format = relationship(
        "Format", back_populates="books", primaryjoin=format_id == Format._id
    )

    def make_uuid(self):
        if not self._uuid:
            self._uuid = uuid.uuid4()


@generic_repr
class Author(OutputMixin, Base):
    __tablename__ = "author"

    _id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(50))
    last_name = sa.Column(sa.String(50))
    middle_name = sa.Column(sa.String(50), nullable=True, default=None)
    prefix = sa.Column(sa.String(20), nullable=True, default=None)
    suffix = sa.Column(sa.String(20), nullable=True, default=None)
    _uuid = sa.Column(sau.UUIDType, unique=True)

    sa.UniqueConstraint(
        "prefix",
        "first_name",
        "middle_name",
        "last_name",
        "suffix",
        name="unique_author",
    )

    books = relationship("Book", back_populates="authors", secondary="book_authors")

    def make_uuid(self):
        if not self._uuid:
            self._uuid = uuid.uuid4()


@generic_repr
class Publisher(OutputMixin, Base):
    __tablename__ = "publisher"

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))

    books = relationship(
        "Book", back_populates="publishers", secondary="book_publishers"
    )


@generic_repr
class SeriesIndex(OutputMixin, Base):
    __tablename__ = "series_index"

    book_id = sa.Column(sa.Integer, sa.ForeignKey("book._id"), primary_key=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey("series._id"), primary_key=True)

    book = relationship("Book", back_populates="series")
    series = relationship("Series", back_populates="books")

    idx = sa.Column(
        sa.Float, sa.CheckConstraint("idx>=0", name="positive_index"), primary_key=True
    )


book_authors = sa.Table(
    "book_authors",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book._id"), primary_key=True),
    sa.Column("author_id", sa.ForeignKey("author._id"), primary_key=True),
)

book_publishers = sa.Table(
    "book_publishers",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book._id"), primary_key=True),
    sa.Column("publisher_id", sa.ForeignKey("publisher._id"), primary_key=True),
)

book_genres = sa.Table(
    "book_genres",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book._id"), primary_key=True),
    sa.Column("genre_id", sa.ForeignKey("genre._id"), primary_key=True),
)

book_languages = sa.Table(
    "book_languages",
    Base.metadata,
    sa.Column("book_id", sa.ForeignKey("book._id"), primary_key=True),
    sa.Column("language_id", sa.ForeignKey("language._id"), primary_key=True),
)
