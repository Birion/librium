from librium.services import SeriesService
from librium.views.views.utils import SeriesType, get_raw


def get_series(args) -> dict[str, list[SeriesType] | int]:
    s = args.get("start").lower() if args.get("start") else ""
    n = args.get("name")
    filters = {
        "start": lambda x: x.name.lower().startswith(s),
        "name": lambda x: x.name == n,
    }
    options = {"series": [], "pagination": None}

    _series, options["pagination"] = get_raw(SeriesService, args, filters)

    for si in _series:
        series_info = {"series": si.name, "books": []}
        for s in si.books:
            series_book = {
                "name": s.book.name,
                "id": s.book.id,
                "idx": s.index,
                "authors": [],
                "published": s.book.released,
                "uuid": s.book.uuid,
            }
            for a in s.book.authors:
                series_book["authors"].append(
                    {"name": a.author.name, "id": a.author.id, "idx": a.idx}
                )
            series_book["authors"].sort(key=lambda x: x["idx"])
            series_info["books"].append(series_book)
        series_info["books"].sort(key=lambda x: x["idx"])
        options["series"].append(series_info)

    return options
