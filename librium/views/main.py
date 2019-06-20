from math import ceil
from types import LambdaType
from typing import Any, Dict, Iterable, List, Tuple, Union

from flask import Blueprint, redirect, render_template, request, url_for
from marshmallow import fields
from webargs.flaskparser import use_args

from librium.database.pony.db import *

bp = Blueprint("main", __name__)

AuthorType = Dict[str, Union[str, List[Dict[str, Any]]]]
SeriesType = Dict[str, Union[str, List[Dict[str, Any]]]]
BookType = Dict[str, Iterable]
YearType = Dict[str, Iterable]

pagesize = 15


def paginate(length: int) -> int:
    return ceil(length / pagesize)


def get_raw(table: db.Entity, args: dict, filters: dict, order: LambdaType = lambda x: x.name) -> Tuple[Iterable, int]:
    items = select(i for i in table)
    page = args.get("page", 1)

    for k, v in filters.items():
        if (k == "default" and v) or args.get(k):
            items = items.filter(v)

    length = count(x for x in items)

    items = items.order_by(order).page(page, pagesize=pagesize)

    if args.get("id"):
        items = [table[args["id"]]]
        length = count(x for x in items)

    return items, paginate(length)


def get_authors(args) -> Dict[str, Union[List[AuthorType], int]]:
    filters = {
        "default": lambda x: not x.books.is_empty(),
        "start": lambda x: x.last_name.lower().startswith(args.get("start").lower()),
        "read": lambda x: len(x.books.filter(lambda b: b.book.read is args.get("read"))) > 0,
        "name": lambda x: x.name == args.get("name"),
    }
    options = {
        "authors": [],
        "pagination": None
    }

    _authors, options["pagination"] = get_raw(Author, args, filters, lambda x: x.last_name)

    def _add_book(book: Book, index: int) -> dict:
        return {
            "book": book.title,
            "id": book.id,
            "year": book.released,
            "read": book.read,
            "idx": index
        }

    for author in _authors:
        s = {"0": []}
        s.update({x: [] for x in {si.name for si in author.books.book.series.series}})
        for _book in author.books:
            book = _book.book
            if not book.series:
                s["0"].append(_add_book(book, -1))
            else:
                for si in book.series:
                    s[si.series.name].append(_add_book(book, si.index))
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
        options["authors"].append(_)

    return options


def get_series(args) -> Dict[str, Union[List[SeriesType], int]]:
    filters = {
        "start": lambda x: x.name.lower().startswith(args.get("start").lower()),
        "name": lambda x: x.name == args.get("name"),
    }
    options = {
        "series": [],
        "pagination": None
    }

    _series, options["pagination"] = get_raw(Series, args, filters)

    for si in _series:
        _ = {"series": si.name, "books": []}
        for s in si.books.order_by(SeriesIndex.idx):
            _2 = {"name": s.book.name, "id": s.book.id, "idx": s.index, "authors": []}
            for a in s.book.authors.order_by(AuthorOrdering.idx):
                _2["authors"].append({"name": a.author.name, "id": a.author.id})
            _["books"].append(_2)
        options["series"].append(_)

    return options


def get_books(args) -> Dict[str, Union[List[BookType], int]]:
    filters = {
        "start": lambda x: x.title.lower().startswith(args.get("start").lower()),
        "name": lambda x: x.title == args.get("name"),
        "read": lambda x: x.read is args.get("read"),
    }
    options = {"books": get_raw(Book, args, filters)[0], "pagination": get_raw(Book, args, filters)[1]}

    return options


def get_years(args) -> Dict[str, Union[List[YearType], int]]:
    page = args.get("page", 1) - 1
    print(page)
    filters = {
        "year": lambda x: x.released == args.get("year")
    }
    options = {
        "years": [{"year": y, "books": select(b for b in Book if b.released == y)} for y in
                  set(select(b.released for b in Book)[:])],
        "pagination": paginate((count(x.released for x in Book)))
    }

    if args.get("year"):
        options["years"] = [x for x in options["years"] if x["year"] == args.get("year")]

    options["years"] = options["years"][pagesize * page:pagesize * (page + 1)]

    return options


user_args = {
    "page": fields.Integer(),
    "start": fields.String(required=False),
    "read": fields.Boolean(),
    "id": fields.Integer(),
    "name": fields.String(),
}


@bp.route("/")
@use_args(user_args)
def index(args):
    def url_for_self(target, **args):
        return url_for(target, **dict(request.args, **args))

    return redirect(url_for_self("main.books"))


@bp.route("/a")
@use_args(user_args)
def authors(args):
    return render_template("main/index.html", **get_authors(args))


@bp.route("/s")
@use_args(user_args)
def series(args):
    return render_template("main/index.html", **get_series(args))


@bp.route("/b")
@use_args(user_args)
def books(args):
    return render_template("main/index.html", **get_books(args))


@bp.route("/y")
@use_args({
    "page": fields.Integer(),
    "year": fields.Integer(),
})
def years(args):
    return render_template("main/index.html", **get_years(args))
