import simplejson as json
import tempfile
from csv import DictWriter
from typing import Literal

from sqlalchemy import select

from librium.database import *

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
    _data["author_details"] = "|".join(
        make_author(author.author) for author in book.authors
    )
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


def run(export_format: Literal["csv", "json"] = "csv") -> str:
    """
    Export book data to a file in the specified format.

    Args:
        export_format: The format to export to ("csv" or "json")

    Returns:
        The path to the exported file
    """
    file_extension = f".{export_format}"
    export_file = tempfile.mkstemp(suffix=file_extension)[1]

    # Get all books
    books = Session.scalars(select(Book).order_by(Book.id)).unique()

    if export_format == "csv":
        with open(export_file, "w", newline="\n") as fp:
            writer = DictWriter(fp, HEADERS)
            writer.writeheader()
            for book in books:
                writer.writerow(process_book_info(book))
    elif export_format == "json":
        book_data = [process_book_info(book) for book in books]
        with open(export_file, "w", encoding="utf-8") as fp:
            json.dump(book_data, fp, indent=2, ensure_ascii=False)

    return export_file


if __name__ == "__main__":
    # Example usage
    csv_file = run("csv")
    print(f"CSV export created at: {csv_file}")

    json_file = run("json")
    print(f"JSON export created at: {json_file}")
