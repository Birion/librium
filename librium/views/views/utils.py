from math import ceil
from typing import Any, Iterable, TypeVar

from librium.services import (
    BookService,
    GenreService,
    SeriesService,
    YearService,
)

AuthorType = dict[str, str | list[dict[str, Any]]]
SeriesType = dict[str, str | list[dict[str, Any]]]
BookType = dict[str, Iterable]
YearType = dict[str, Iterable]
GenreType = dict[str, Iterable]

# Type variable for a generic entity type
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


def get_pagesize(service: Any) -> int:
    """
    Get the page size for a given service.
    This is used to determine how many items to display per page.
    """
    if service == BookService:
        return pagesize
    return 10  # Default page size for other services


def get_raw(
    service,
    arguments: dict,
    filters: dict,
    sorting_key=lambda x: x.name,
) -> tuple[list | dict[str, list] | None, int]:
    # Handle direct ID lookup first
    if arguments.get("id"):
        item = service.get_by_id(arguments["id"])
        paginated_items = [item] if item else []
        length = len(paginated_items)
        return paginated_items, paginate(length)

    # Get the current page
    page = arguments.get("page", 1)

    # Determine read filter
    read_filter = None
    if "read" in arguments:
        read_filter = arguments["read"]

    # Determine search filter
    search = arguments.get("search")

    # Determine start_with filter
    start_with = None
    if "start" in arguments and arguments["start"]:
        start_with = arguments["start"].lower()

    # Determine the exact_name filter
    exact_name = arguments.get("name")

    # Determine sorting options
    sort_by = arguments.get("sort_by", "title")
    sort_order = arguments.get("sort_order", "asc")

    pagesize = get_pagesize(service)

    if service == BookService or service == GenreService or service == SeriesService or service == YearService:
        # Get paginated books
        paginated_items, total_count = service.get_paginated(
            page=page,
            page_size=pagesize,
            filter_read=read_filter,
            search=search,
            start_with=start_with,
            exact_name=exact_name,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        paginated_length = ceil(total_count / pagesize)
        if service == GenreService:
            paginated_items = {
                key.name: GenreService.get_books_in_genre_formatted(key.id)
                for key in paginated_items
            }
        if service == SeriesService:
            paginated_items = {
                key.name: SeriesService.get_books_in_series_formatted(key.id)
                for key in paginated_items
            }
        if service == YearService:
            years = [year for year in {key.released for key in paginated_items}]
            years.sort()
            paginated_items = {
                year: YearService.get_books_in_year_formatted(year)
                for year in years
            }
    else:
        # For other services, use the original in-memory pagination
        # Get all items using the service
        items = service.get_all()

        # Apply filters
        items = apply_filters(filters, arguments, items) if filters else items
        sorted_items = sorted(items, key=sorting_key)
        paginated_items = apply_pagination(arguments.get("page", 1), sorted_items)
        paginated_length = len(paginated_items)

    return paginated_items, paginated_length
