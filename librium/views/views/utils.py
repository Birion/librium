from math import ceil
from typing import Any, Iterable, Tuple

from librium.database.pony.db import *

AuthorType = dict[str, str | list[dict[str, Any]]]
SeriesType = dict[str, str | list[dict[str, Any]]]
BookType = dict[str, Iterable]
YearType = dict[str, Iterable]
GenreType = dict[str, Iterable]

pagesize = 15


def paginate(length: int) -> int:
    return ceil(length / pagesize)


def apply_filters(filters, arguments, items):
    valid_filters = [v for k, v in filters.items() if (k == "default" and v) or k in arguments.keys()]
    return [item for item in items if all(valid_filter(item) for valid_filter in valid_filters)]


def apply_pagination(page, items):
    start, end = (page - 1) * pagesize, page * pagesize
    return items[start:end]


def get_raw(
        table: db.Entity,
        arguments: dict,
        filters: dict,
        attribute: str = "name",
        sorting_key=lambda x: x.name,
) -> Tuple[list | None, list[str], int]:
    items = table.select()

    items = apply_filters(filters, arguments, items) if filters else items
    length = len(items)
    sorted_items = sorted(items, key=sorting_key)
    paginated_items = apply_pagination(arguments.get("page", 1), sorted_items)

    start_filter = f"x.{attribute} for x in {table.__name__}"
    initial_letters = sorted({x[0].lower() for x in select(start_filter)})

    if arguments.get("id"):
        paginated_items = [table[arguments["id"]]]
        length = count(x for x in paginated_items)

    return paginated_items, initial_letters, paginate(length)
