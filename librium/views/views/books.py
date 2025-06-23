from librium.services import BookService
from librium.views.views.utils import BookType, get_raw


def get_books(args) -> dict[str, list[BookType] | int]:
    # All filtering is now handled at the database level in get_raw for BookService
    # No need to define filters here

    # Get books using the service
    results = get_raw(BookService, args, {}, "title")
    options = {"books": results[0], "pagination": results[2], "letters": results[1]}

    return options
