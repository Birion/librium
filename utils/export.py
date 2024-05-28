from csv import DictWriter

from librium.database.pony.db import *

HEADERS = [
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


def make_author(author: Author) -> str:
    p = author.prefix or ""
    f = author.first_name or ""
    m = author.middle_name or ""
    l = author.last_name or ""
    s = author.suffix or ""
    return f"{l} {s}, {p} {f} {m}".replace("  ", " ").replace(" ,", ",").strip()


def make_series(series: SeriesIndex, decimal_places: int = 0) -> str:
    series_name = series.series.name
    has_decimal_part = (series.idx * 10) % 10 != 0
    index = round(series.idx, decimal_places) if has_decimal_part else int(series.idx)
    return f"{series_name} ({index})" if index else series_name


def process_book_info(book):
    _data: dict[str, None | str | int | float] = {k: None for k in HEADERS}
    _data["author_details"] = "|".join(make_author(author.author) for author in book.authors)
    _data["title"] = book.title
    _data["isbn"] = book.isbn
    _data["publisher"] = "|".join(pub.name for pub in book.publishers)
    _data["date_published"] = book.released
    _data["read"] = 1 if book.read else 0
    _data["series_details"] = "|".join(make_series(series) for series in book.series)
    _data["pages"] = book.page_count
    _data["list_price"] = book.price
    _data["format"] = book.format.name
    _data["genre"] = "|".join(genre.name for genre in book.genres)
    _data["language"] = "|".join(lang.name for lang in book.languages)
    _data["book_uuid"] = book.hex_uuid
    return _data


@db_session
def run():
    with open("export.csv", "w", newline="\n") as fp:
        writer = DictWriter(fp, HEADERS)
        writer.writeheader()
        for book in Book.select().order_by(Book.id):
            writer.writerow(process_book_info(book))


if __name__ == "__main__":
    run()
