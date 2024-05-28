from librium.database.pony.db import *
from librium.views.views.utils import BookType, get_raw


def get_books(args) -> dict[str, list[BookType] | int]:
    s = args.get("start").lower() if args.get("start") else ""
    n = args.get("name")
    r = args.get("read")
    filters = {}
    if s:
        filters["start"] = lambda x: x.title.lower().startswith(s)
    if n:
        filters["name"] = lambda x: x.title == n
    if r:
        filters["read"] = lambda x: x.read is r
    _ = get_raw(Book, args, filters, "title")
    options = {"books": _[0], "pagination": _[2], "letters": _[1]}

    return options
