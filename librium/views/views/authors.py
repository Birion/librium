from librium.services import BookService, AuthorService, SeriesService
from librium.views.views.utils import AuthorType, get_raw


def add_book(book, index: int) -> dict:
    return {
        "book": book.title,
        "id": book.id,
        "year": book.released,
        "read": book.read,
        "idx": index,
        "uuid": book.uuid,
    }


def get_read(author, series_name) -> int:
    # Get series by name
    series_list = [s for s in SeriesService.get_all() if s.name == series_name]
    series = series_list[0] if series_list else None

    if series:
        # Get books in series that are read and have this author
        books_in_series = SeriesService.get_books_in_series(series.id)
        books = [
            b
            for b in books_in_series
            if b.read and any(a.author_id == author.id for a in b.authors)
        ]
    else:
        # Get standalone books by this author that are read
        author_books = [
            b.book for b in author.books if b.book.read and not b.book.series
        ]
        books = author_books

    return len(books)


def get_unread(author, series_name) -> int:
    # Get series by name
    series_list = [s for s in SeriesService.get_all() if s.name == series_name]
    series = series_list[0] if series_list else None

    if series:
        # Get books in series that are unread and have this author
        books_in_series = SeriesService.get_books_in_series(series.id)
        books = [
            b
            for b in books_in_series
            if not b.read and any(a.author_id == author.id for a in b.authors)
        ]
    else:
        # Get standalone books by this author that are unread
        author_books = [
            b.book for b in author.books if not b.book.read and not b.book.series
        ]
        books = author_books

    return len(books)


def get_author_series(srs, books, author) -> dict:
    return {
        "series": srs,
        "status": {"read": get_read(author, srs), "unread": get_unread(author, srs)},
        "books": books,
    }


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

    # Get authors using the service
    authors, options["pagination"] = get_raw(
        AuthorService, args, filters, lambda x: x.last_name
    )

    for author in authors:
        # Initialise series dictionary with standalone books
        authors_series = {"0": []}

        # Get all series names for this author's books
        series_names = set()
        for book_author in author.books:
            book = book_author.book
            for series_index in book.series:
                series_names.add(series_index.series.name)

        # Add series names to the dictionary
        authors_series.update({name: [] for name in series_names})

        # Process each book
        for book_author in author.books:
            book = book_author.book
            if not book.series:
                # Add standalone book
                authors_series["0"].append(add_book(book, -1))
            else:
                # Add book to each series it belongs to
                for series_index in book.series:
                    authors_series[series_index.series.name].append(
                        add_book(book, series_index.idx)
                    )

        # Remove empty standalone books list
        if not authors_series["0"]:
            del authors_series["0"]

        # Sort books in each series
        for series_name in authors_series:
            authors_series[series_name].sort(key=lambda x: x["book"])
            authors_series[series_name].sort(key=lambda x: x["idx"])

        # Create author data
        author_data = {
            "author": author.name,
            "series": [
                get_author_series(x, authors_series[x], author) for x in authors_series
            ],
            "books": author.books,
        }
        author_data["series"].sort(key=lambda x: x["series"])
        options["authors"].append(author_data)

    return options
