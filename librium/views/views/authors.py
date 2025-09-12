from librium.services import BookService, AuthorService, SeriesService
from librium.views.views.utils import AuthorType, get_raw


def get_authors(args) -> dict[str, list[AuthorType] | int]:
    start = args.get("start").lower() if args.get("start") else ""
    name = args.get("name")
    is_read = args.get("read")

    # Define filters for authors
    filters = {
        "default": lambda x: len(x.books) > 0,  # Author has books
        "read": lambda x: any(
            b.book.read is is_read for b in x.books
        ),  # Author has books with specified read status
    }

    if start:
        filters["start"] = lambda x: x.last_name.lower().startswith(start)
    if name:
        filters["name"] = lambda x: x.name == name

    options = {"authors": [], "pagination": None}

    # Get authors using the service (paginated)
    authors, options["pagination"] = get_raw(
        AuthorService, args, filters, lambda x: x.last_name
    )

    # Delegate formatting to the AuthorService to match service-based approach
    options["authors"] = AuthorService.format_authors(authors)

    return options
