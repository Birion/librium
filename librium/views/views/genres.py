from librium.database.pony.db import *
from librium.views.views.utils import GenreType, get_raw


def get_genres(args) -> dict[str, list[GenreType] | int]:
    filters = {
        "start": lambda x: x.name.lower().startswith(args.get("start").lower()),
        "name": lambda x: x.name == args.get("name"),
    }
    result = get_raw(Genre, args, filters)
    options = {"genres": {}, "pagination": result[2], "letters": result[1]}
    for genre in result[0]:
        options["genres"][genre.name] = select(b for b in Book if genre in b.genres).order_by(Book.title)[:]

    return options
