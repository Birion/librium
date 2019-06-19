from math import ceil
from typing import Any, Tuple

from flask import Blueprint, render_template
from marshmallow import fields
from webargs.flaskparser import use_args

from librium.database.pony.db import *

bp = Blueprint("main", __name__)


def get_authors(args) -> Tuple[Any, int]:
    page = args.get("page", 1)
    pagesize = 15

    authors = []
    _authors = Author.select(lambda a: not a.books.is_empty())
    if args.get("start"):
        _authors = _authors.filter(lambda a: a.last_name.lower().startswith(args.get("start").lower()))

    if "read" in args.keys():
        _authors = _authors.filter(lambda a: len(a.books.filter(lambda b: b.book.read is args.get("read"))) > 0)

    for author in _authors.order_by(Author.last_name).page(page, pagesize=pagesize):
        s = {"0": []}
        s.update({x: [] for x in {series.name for series in author.books.book.series.series}})
        for _book in author.books:
            book = _book.book
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

        def _read(series) -> int:
            return count(si for si in Series.get(name=series).books_read if author in si.book.authors) if Series.get(
                name=series) else count(b for b in author.books_standalone if b.read)

        def _unread(series) -> int:
            return count(si for si in Series.get(name=series).books_unread if author in si.book.authors) if Series.get(
                name=series) else count(b for b in author.books_standalone if not b.read)

        def _series(series, books) -> dict:
            return {
                "series": series,
                "status": {
                    "read": _read(series),
                    "unread": _unread(series)
                },
                "books": books
            }

        _ = {"author": author.name, "series": [_series(x, s[x]) for x in s]}
        _["series"].sort(key=lambda x: x["series"])
        authors.append(_)
        print(_)

    max_length = ceil(count(a for a in _authors) / pagesize)
    return authors, max_length


user_args = {
    "page": fields.Integer(),
    "start": fields.String(required=False),
    "read": fields.Boolean(),
}


@bp.route("/")
@use_args(user_args)
def index(args):
    authors, max_length = get_authors(args)
    return render_template("main/index.html", authors=authors, pagination=max_length)


@bp.route("/a")
@use_args(user_args)
def authors(args):
    a, max_length = get_authors(args)

    options = {
        "authors": a,
        "pagination": max_length
    }

    return render_template("main/index.html", **options)


@bp.route("/s")
@use_args(user_args)
def series(args):
    pass
