from librium.services import BookService
from librium.views.views.utils import BookType, get_raw


def get_books(args) -> dict[str, list[BookType] | int]:
    s = args.get("start").lower() if args.get("start") else ""
    n = args.get("name")
    r = args.get("read")
    search = args.get("search")

    # Define filters for books
    filters = {
        "read": lambda x: x.read is r,
        "search": lambda x: (
            x.title.lower().find(search.lower()) >= 0 if search else True
        ),
    }
    if s:
        filters["start"] = lambda x: x.title.lower().startswith(s)
    if n:
        filters["name"] = lambda x: x.title == n

    # Get books using the service
    results = get_raw(BookService, args, filters, "title")
    options = {"books": results[0], "pagination": results[2], "letters": results[1]}

    return options
