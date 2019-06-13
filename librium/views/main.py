from typing import Any, Tuple

from flask import Blueprint, render_template
from marshmallow import fields
from pony.orm import *
from webargs.flaskparser import use_args

from librium.database.pony.db import Author

bp = Blueprint("main", __name__)


def get_authors(args) -> Tuple[Any, int]:
    page = args.get("page", 1)

    authors = []

    for author in Author.select().order_by(Author.last_name).page(page):
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

    max_length = int(count(a for a in Author) / 10)
    return authors, max_length


@bp.route("/")
@use_args({
    "page": fields.Integer()
})
def index(args):
    authors, max_length = get_authors(args)
    return render_template("main/index.html", authors=authors, pagination=max_length)
