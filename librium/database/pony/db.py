import os
import uuid

from dotenv import find_dotenv, load_dotenv
from pony.orm import *

load_dotenv(find_dotenv())

db = Database(provider="sqlite", filename=os.getenv("PONY_SQLDATABASE"), create_db=True)


class Book(db.Entity):
    _table_ = "book"
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    isbn = Optional(str, 13)
    released = Optional(int, size=64)
    page_count = Optional(int, size=64)
    price = Optional(float)
    read = Required(bool, default=False)
    has_cover = Required(bool, default=False)
    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))

    authors = Set("Author", table="book_authors")
    publishers = Set("Publisher", table="book_publishers")
    format = Required("Format")
    languages = Set("Language", table="book_languages")
    genres = Set("Genre", table="book_genres")
    series = Set("SeriesIndex")


class Author(db.Entity):
    _table_ = "author"
    id = PrimaryKey(int, auto=True)
    first_name = Optional(str, 50)
    middle_name = Optional(str, 50)
    last_name = Optional(str, 50)
    prefix = Optional(str, 20)
    suffix = Optional(str, 20)
    name = Required(str)
    uuid = Required(str, unique=True, default=lambda: str(uuid.uuid4()))

    books = Set(Book)


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


class SeriesIndex(db.Entity):
    _table_ = "series_index"
    book = Required(Book)
    series = Required(Series)
    idx = Required(float, default=0)
    PrimaryKey(book, series)

    @property
    def index(self):
        return int(self.idx) if not self.idx * 10 % 10 else self.idxk


db.generate_mapping(create_tables=True)
