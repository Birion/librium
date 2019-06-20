from flask import Blueprint, redirect, render_template, request, url_for
from webargs.flaskparser import use_args

from librium.database.pony.db import *
from librium.views.utilities import BookSchema

bp = Blueprint("book", __name__, url_prefix="/book")


def add_or_update(book: Book, args):
    lookup_table = {
        "genres": Genre,
        "publishers": Publisher,
        "languages": Language
    }

    def parse(table, key):
        return table[key]

    for k, v in lookup_table.items():
        if args.get(k):
            args[k] = [v[i] for i in args[k]]
    args["format"] = Format[args["format"]]
    _series = []
    for s in args["series"]:
        try:
            si = SeriesIndex[book.id, s["series"]]
        except ObjectNotFound:
            si = SeriesIndex(book=book, series=Series[s["series"]])
        si.idx = s["idx"]
        _series.append(si)
    _authors = []
    i = 1
    for a in args["authors"]:
        try:
            ax = AuthorOrdering[book.id, a]
        except ObjectNotFound:
            ax = AuthorOrdering(book=book, author=Author[a])
        ax.idx = i
        i += 1
        _authors.append(ax)
    args["series"] = _series
    args["authors"] = _authors

    book.set(**args)
    commit()


@bp.route("/<int:id>", methods=["GET", "POST"])
@use_args(BookSchema)
def index(args, id):
    if request.method == "POST":
        print(args)
        book = Book[id]

        add_or_update(book, args)

        return redirect(url_for("book.index", id=id))
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
@use_args(BookSchema)
def add(args):
    if request.method == "POST":
        book = Book(title="x")
        commit()
        add_or_update(book, args)
        return redirect(url_for("book.index", id=book.id))
    options = {
        "genres": Genre.select().order_by(Genre.name),
        "formats": Format.select().order_by(Format.name),
        "languages": Language.select().order_by(Language.name),
        "publishers": Publisher.select().order_by(Publisher.name),
        "series": Series.select().order_by(Series.name),
        "authors": Author.select(lambda a: not a.books.is_empty()).order_by(Author.last_name),
    }
    return render_template("book/index.html", **options)
