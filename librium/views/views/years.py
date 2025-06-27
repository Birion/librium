from librium.database import *
from librium.views.views.utils import YearType, pagesize, paginate


def get_years(args) -> dict[str, list[YearType] | int]:
    page = args.get("page", 1) - 1
    options = {
        "years": [],
        "pagination": paginate((count(x.released for x in Book))),
        "all_years": {x for x in select(b.released for b in Book if b.released)},
    }

    if args.get("year"):
        options["years"] = [
            {
                "year": args.get("year"),
                "books": Book.select(lambda b: b.released == args.get("year")),
            }
        ]
    else:
        options["years"] = [
            {"year": y, "books": select(b for b in Book if b.released == y)}
            for y in {x.released for x in Book.select().order_by(Book.released)}
        ]

    options["years"] = options["years"][pagesize * page : pagesize * (page + 1)]

    return options


def get_years(args) -> dict[str, YearType | int]:
    is_read = args.get("read")

    filters = {
        "read": lambda x: any(b.book.read is is_read for b in x.books),
    }

    options = {"years": [], "pagination": None}
