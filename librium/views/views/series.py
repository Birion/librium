from librium.database.pony.db import *
from librium.views.views.utils import SeriesType, get_raw


def get_series(args) -> dict[str, list[SeriesType] | int]:
    s = args.get("start").lower() if args.get("start") else ""
    n = args.get("name")
    filters = {
        "start": lambda x: x.name.lower().startswith(s),
        "name": lambda x: x.name == n,
    }
    options = {"series": [], "pagination": None, "letters": {}}

    _series, options["letters"], options["pagination"] = get_raw(Series, args, filters)

    for si in _series:
        _ = {"series": si.name, "books": []}
        for s in si.books.order_by(SeriesIndex.idx):
            _2 = {"name": s.book.name, "id": s.book.id, "idx": s.index, "authors": [], "published": s.book.released,
                  "uuid": s.book.uuid}
            for a in s.book.authors.order_by(AuthorOrdering.idx):
                _2["authors"].append({"name": a.author.name, "id": a.author.id})
            _["books"].append(_2)
        options["series"].append(_)

    return options
