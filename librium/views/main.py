from math import ceil
from typing import Any, Tuple

from flask import Blueprint, render_template, request
from marshmallow import fields
from pony.orm import *
from webargs.flaskparser import use_args

from librium.database.pony.db import Author

bp = Blueprint("main", __name__)


def get_authors(args) -> Tuple[Any, int]:
    page = args.get("page", 1)
    pagesize = 15

    authors = []
    _authors = Author.select(lambda a: len(a.books) > 0)
    if args.get("start"):
        _authors = _authors.filter(lambda a: a.last_name.lower().startswith(args.get("start").lower()))

    for author in _authors.order_by(Author.last_name).page(page, pagesize=pagesize):
        s = {"0": []}
        s.update({x: [] for x in {series.name for series in author.books.series.series}})
        for book in author.books:
            if not book.series:
                s["0"].append(
                    {
                        "book": book.title,
                        "id": book.id,
                        "year": book.released,
                        "read": book.read,
                        "idx": -1
                    }
                )
            else:
                for series in book.series:
                    s[series.series.name].append(
                        {
                            "book": book.title,
                            "id": book.id,
                            "year": book.released,
                            "read": book.read,
                            "idx": series.index
                        }
                    )
        if not s["0"]:
            del s["0"]

        for sx in s:
            s[sx].sort(key=lambda x: x["book"])
            s[sx].sort(key=lambda x: x["idx"])

        _ = {"author": author.name, "series": [{"series": x, "books": s[x]} for x in s]}
        _["series"].sort(key=lambda x: x["series"])
        authors.append(_)

    max_length = ceil(count(a for a in _authors) / pagesize)
    return authors, max_length


@bp.route("/")
@use_args({
    "page": fields.Integer(),
    "start": fields.String(required=False),
})
def index(args):
    authors, max_length = get_authors(args)
    return render_template("main/index.html", authors=authors, pagination=max_length)
