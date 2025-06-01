from math import ceil
from typing import Any, Iterable, Tuple, List, Callable, TypeVar, Generic, Dict

from librium.services import (
    BookService,
    FormatService,
    GenreService,
    LanguageService,
    PublisherService,
    SeriesService,
    AuthorService,
)

AuthorType = dict[str, str | list[dict[str, Any]]]
SeriesType = dict[str, str | list[dict[str, Any]]]
BookType = dict[str, Iterable]
YearType = dict[str, Iterable]
GenreType = dict[str, Iterable]

# Type variable for generic entity type
T = TypeVar("T")

pagesize = 30


def paginate(length: int) -> int:
    return ceil(length / pagesize)


def apply_filters(filters, arguments, items):
    valid_filters = [
        v for k, v in filters.items() if (k == "default" and v) or k in arguments.keys()
    ]
    return [
        item
        for item in items
        if all(valid_filter(item) for valid_filter in valid_filters)
    ]


def apply_pagination(page, items):
    start, end = (page - 1) * pagesize, page * pagesize
    return items[start:end]


def get_raw(
    service,
    arguments: dict,
    filters: dict,
    attribute: str = "name",
    sorting_key=lambda x: x.name,
) -> Tuple[list | None, list[str], int]:
    # Get all items using the service
    items = service.get_all()

    # Apply filters
    items = apply_filters(filters, arguments, items) if filters else items
    length = len(items)
    sorted_items = sorted(items, key=sorting_key)
    paginated_items = apply_pagination(arguments.get("page", 1), sorted_items)

    # Get initial letters for pagination
    initial_letters = sorted(
        {
            getattr(x, attribute)[0].lower()
            for x in items
            if hasattr(x, attribute) and getattr(x, attribute)
        }
    )

    # Handle direct ID lookup
    if arguments.get("id"):
        item = service.get_by_id(arguments["id"])
        paginated_items = [item] if item else []
        length = len(paginated_items)

    return paginated_items, initial_letters, paginate(length)
