from librium.services import GenreService, BookService
from librium.views.views.utils import GenreType, get_raw


def get_genres(args) -> dict[str, list[GenreType] | int]:
    # Define filters for genres
    filters = {}
    if args.get("start"):
        filters["start"] = lambda x: x.name.lower().startswith(
            args.get("start").lower()
        )
    if args.get("name"):
        filters["name"] = lambda x: x.name == args.get("name")

    # Get genres using the service
    result = get_raw(GenreService, args, filters)
    options = {"genres": {}, "pagination": result[2], "letters": result[1]}

    # Get all books
    all_books = BookService.get_all()

    # For each genre, find books that have that genre
    for genre in result[0]:
        # Filter books by genre and sort by title
        genre_books = [b for b in all_books if any(g.id == genre.id for g in b.genres)]
        genre_books.sort(key=lambda b: b.title)
        options["genres"][genre.name] = genre_books

    return options
