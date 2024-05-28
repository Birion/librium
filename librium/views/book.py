from flask import Blueprint, jsonify, render_template, request, url_for
from webargs.flaskparser import use_args, use_kwargs

from librium.database.pony.db import *
from librium.views.utilities import BookSchema

bp = Blueprint("book", __name__, url_prefix="/book")


def add_or_update(book: Book, args):
    print(args)
    lookup_table = {"genres": Genre, "publishers": Publisher, "languages": Language}

    book.authors = []
    book.series = []

    for k, v in lookup_table.items():
        if args.get(k):
            args[k] = [v[i] for i in args[k]]
    args["format"] = Format[args["format"]]
    _series = []
    for s in args["series"]:
        try:
            si = SeriesIndex[book.id, s["series"], s["idx"]]
        except ObjectNotFound:
            si = SeriesIndex(book=book, series=Series[s["series"]], idx=s["idx"])
        _series.append(si)
    _authors = []
    i = 1
    for a in args["authors"]:
        try:
            ax = AuthorOrdering[book.id, a]
            ax.idx = i
        except ObjectNotFound:
            ax = AuthorOrdering(book=book, author=Author[a], idx=i)
        i += 1
        _authors.append(ax)
    args["series"] = _series
    args["authors"] = _authors

    book.set(**args)
    commit()


@bp.route("/<int:id>", methods=["GET", "POST"])
@use_kwargs(BookSchema, location="form")
def index(id, **kwargs):
    if request.method == "POST":
        print(kwargs)
        book = Book[id]

        add_or_update(book, kwargs)

        return jsonify({"url": url_for("book.index", id=id)})
    options = {
        "book": Book[id],
        "genres": Genre.select().order_by(Genre.name),
        "formats": Format.select().order_by(Format.name),
        "languages": Language.select().order_by(Language.name),
        "publishers": Publisher.select().order_by(Publisher.name),
        "series": Series.select().order_by(Series.name),
        "authors": Author.select().order_by(Author.last_name),
    }
    return render_template("book/index.html", **options)


@bp.route("/add", methods=["GET", "POST"])
@use_args(BookSchema, location="form")
def add(args):
    print(args)
    if request.method == "POST":
        book = Book(title="x")
        add_or_update(book, args)
        return jsonify({"url": url_for("book.index", id=book.id)})
    options = {
        "genres": Genre.select().order_by(Genre.name),
        "formats": Format.select().order_by(Format.name),
        "languages": Language.select().order_by(Language.name),
        "publishers": Publisher.select().order_by(Publisher.name),
        "series": Series.select().order_by(Series.name),
        "authors": Author.select().order_by(Author.last_name),
    }
    return render_template("book/index.html", **options)
