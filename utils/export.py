from csv import DictWriter

from librium.database.pony.db import *

headers = [
    "_id",
    "author_details",
    "title",
    "isbn",
    "publisher",
    "date_published",
    "rating",
    "bookshelf_id",
    "bookshelf",
    "read",
    "series_details",
    "pages",
    "notes",
    "list_price",
    "anthology",
    "location",
    "read_start",
    "read_end",
    "format",
    "signed",
    "loaned_to",
    "anthology_titles",
    "description",
    "genre",
    "language",
    "date_added",
    "goodreads_book_id",
    "last_goodreads_sync_date",
    "last_update_date",
    "book_uuid",
]
template = {k: None for k in headers}


def make_author(author: Author) -> str:
    p = author.prefix or ""
    f = author.first_name or ""
    m = author.middle_name or ""
    l = author.last_name or ""
    s = author.suffix or ""
    return f"{l} {s}, {p} {f} {m}".replace("  ", " ").replace(" ,", ",").strip()


def make_series(series: SeriesIndex) -> str:
    name = series.series.name
    idx = series.idx if series.idx * 10 % 10 else int(series.idx)
    return f"{name} ({idx})" if idx else name


@db_session
def run():
    with open("export.csv", "w") as fp:
        writer = DictWriter(fp, headers)
        writer.writeheader()
        for book in Book.select().order_by(Book.id):
            _data = template.copy()
            _data["author_details"] = "|".join(make_author(author.author) for author in book.authors)
            _data["title"] = book.title
            _data["isbn"] = book.isbn
            _data["publisher"] = "|".join(pub.name for pub in book.publishers)
            _data["date_published"] = book.released
            # _data["rating"] = 0
            # _data["bookshelf_id"] = 1
            # _data["bookshelf"] = "Default"
            _data["read"] = 1 if book.read else 0
            _data["series_details"] = "|".join(make_series(series) for series in book.series)
            _data["pages"] = book.page_count
            # "notes",
            _data["list_price"] = book.price
            # "anthology",
            # "location",
            # "read_start",
            # "read_end",
            _data["format"] = book.format.name
            # "signed",
            # "loaned_to",
            # "anthology_titles",
            # "description",
            _data["genre"] = "|".join(genre.name for genre in book.genres)
            _data["language"] = "|".join(lang.name for lang in book.languages)
            # "date_added",
            # "goodreads_book_id",
            # "last_goodreads_sync_date",
            # "last_update_date",
            _data["book_uuid"] = book.hex_uuid
            writer.writerow(_data)


if __name__ == '__main__':
    run()
