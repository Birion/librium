import os
import uuid
from decimal import Decimal

from dotenv import find_dotenv, load_dotenv
from pony.orm import *

load_dotenv(find_dotenv())

db_file = os.getenv("PONY_SQLDATABASE")

db = Database(provider="sqlite", filename=db_file, create_db=True)


class Book(db.Entity):
    _table_ = "book"
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    isbn = Optional(str, 13)
    released = Optional(int, size=64)
    page_count = Optional(int, size=64)
    price = Optional(Decimal)
    read = Required(bool, default=False)
    has_cover = Required(bool, default=False)
    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))

    authors = Set("AuthorOrdering")
    publishers = Set("Publisher", table="book_publishers")
    format = Required("Format", default=1)
    languages = Set("Language", table="book_languages")
    genres = Set("Genre", table="book_genres")
    series = Set("SeriesIndex")

    @property
    def hex_uuid(self):
        return uuid.UUID(self.uuid).hex

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @property
    def authors_deep(self):
        return [a.author for a in self.authors.select().order_by(AuthorOrdering.idx)]

    @property
    def a_id(self):
        return [a.author.id for a in self.authors.select().order_by(AuthorOrdering.idx)]

    @property
    def g_id(self):
        return [g.id for g in self.genres.select()]

    @property
    def p_id(self):
        return [p.id for p in self.publishers.select()]

    @property
    def l_id(self):
        return [l.id for l in self.languages.select()]

    @property
    def s_id(self):
        return [s.series.id for s in self.series.select()]


class Author(db.Entity):
    _table_ = "author"
    id = PrimaryKey(int, auto=True)
    first_name = Optional(str, 50, default=None, nullable=True)
    middle_name = Optional(str, 50, default=None, nullable=True)
    last_name = Optional(str, 50, default=None, nullable=True)
    prefix = Optional(str, 20, default=None, nullable=True)
    suffix = Optional(str, 20, default=None, nullable=True)
    name = Optional(str)
    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))

    books = Set("AuthorOrdering")

    def make_uuid(self):
        self.uuid = str(uuid.uuid4())

    @property
    def books_in_series(self):
        return select(b.book for b in self.books if not b.book.series.is_empty())

    @property
    def books_standalone(self):
        return select(b.book for b in self.books if b.book.series.is_empty())


class Publisher(db.Entity):
    _table_ = "publisher"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50)

    books = Set(Book)


class Format(db.Entity):
    _table_ = "format"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50)

    books = Set(Book)


class Language(db.Entity):
    _table_ = "language"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50)

    books = Set(Book)


class Genre(db.Entity):
    _table_ = "genre"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50)

    books = Set(Book)


class Series(db.Entity):
    _table_ = "series"
    id = PrimaryKey(int, auto=True)
    name = Required(str, 50, unique=True)

    books = Set("SeriesIndex")

    @property
    def has_unread_books(self):
        return len(self.books.filter(lambda si: si.book.read is False)) > 0

    @property
    def has_read_books(self):
        return len(self.books.filter(lambda si: si.book.read is True)) > 0

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
    PrimaryKey(book, series, idx)

    @property
    def index(self):
        return int(self.idx) if not self.idx * 10 % 10 else self.idx


class AuthorOrdering(db.Entity):
    _table_ = "book_authors"
    book = Required(Book)
    author = Required(Author)
    idx = Required(int, default=0)
    PrimaryKey(book, author)
    composite_index(book, idx)


db.generate_mapping(create_tables=True)
