from librium.services import GenreService, BookService
from librium.views.views.utils import GenreType, get_raw


def get_genres(args) -> dict[str, list[GenreType] | int]:
    # Define filters for genres
    s = args.get("start").lower() if args.get("start") else ""
    n = args.get("name")
    filters = {
        "start": lambda x: x.name.lower().startswith(s),
        "name": lambda x: x.name == n,
    }
    options = {"genres": {}, "pagination": None, "letters": {}}

    # Get genres using the service
    _genres, options["letters"], options["pagination"] = get_raw(
        GenreService, args, filters
    )

    # For each genre, find books that have that genre
    for genre in _genres:
        genre_books = []
        for b in genre.books:
            book_info = {
                "name": b.title,
                "id": b.id,
                "uuid": b.uuid,
                "authors": [],
                "series": [],
                "released": b.released,
            }
            for s in b.series:
                book_info["series"].append(
                    {"name": s.series.name, "id": s.series.id, "idx": s.idx}
                )
            for a in b.authors:
                book_info["authors"].append(
                    {"name": a.author.name, "id": a.author.id, "idx": a.idx}
                )
            book_info["authors"].sort(key=lambda x: x["idx"])
            genre_books.append(book_info)

        sorted_list = sorted(
            genre_books,
            key=lambda x: x.get("series")[0]["name"] if x.get("series") else "",
        )
        print(sorted_list)
        try:
            genre_books.sort(
                key=lambda x: (
                    x["series"][0]["name"] if x.get("series") else "",
                    x["series"][0]["idx"] if x.get("series") else 0,
                    x["name"],
                )
            )
        except IndexError:
            genre_books.sort(key=lambda x: x["name"])
        options["genres"][genre.name] = genre_books

    return options
