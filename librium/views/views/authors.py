from librium.database.pony.db import *
from librium.views.views.utils import AuthorType, get_raw


def add_book(book: Book, index: int) -> dict:
    return {
        "book": book.title,
        "id": book.id,
        "year": book.released,
        "read": book.read,
        "idx": index,
        "uuid": book.uuid,
    }


def get_read(author: Author, series_name) -> int:
    series = Series.get(name=series_name)
    if series:
        books = (si for si in series.books_read if author in si.book.authors.author)
    else:
        books = (b for b in author.books_standalone if b.read)
    return count(books)


def get_unread(author, series_name) -> int:
    series = Series.get(name=series_name)
    if series:
        books = (si for si in series.books_unread if author in si.book.authors.author)
    else:
        books = (b for b in author.books_standalone if not b.read)
    return count(books)


def get_author_series(srs, books, author) -> dict:
    return {
        "series": srs,
        "status": {"read": get_read(author, srs), "unread": get_unread(author, srs)},
        "books": books,
    }


def get_authors(args) -> dict[str, list[AuthorType] | int]:
    start = args.get("start").lower() if args.get("start") else ""
    name = args.get("name")
    is_read = args.get("read")

    filters = {
        "default": lambda x: not x.books.is_empty(),
        "read": lambda x: len(x.books.filter(lambda b: b.book.read is is_read)) > 0,
    }

    if start:
        filters["start"] = lambda x: x.last_name.lower().startswith(start)
    if name:
        filters["name"] = lambda x: x.name == name

    options = {"authors": [], "pagination": None, "letters": {}}
    authors, options["letters"], options["pagination"] = get_raw(
        Author, args, filters, "last_name", lambda x: x.last_name
    )

    for author in authors:
        authors_series = {"0": []}
        authors_series.update({x: [] for x in {si.name for si in author.books.book.series.series}})
        for _book in author.books:
            book = _book.book
            if not book.series:
                authors_series["0"].append(add_book(book, -1))
            else:
                for si in book.series:
                    authors_series[si.series.name].append(add_book(book, si.index))
        if not authors_series["0"]:
            del authors_series["0"]
        for series_name in authors_series:
            authors_series[series_name].sort(key=lambda x: x["book"])
            authors_series[series_name].sort(key=lambda x: x["idx"])
        author_data = {"author": author.name, "series": [get_author_series(x, authors_series[x], author) for x in authors_series], "books": author.books}
        author_data["series"].sort(key=lambda x: x["series"])
        options["authors"].append(author_data)

    return options


