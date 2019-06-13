from flask import Blueprint, render_template, request, redirect, url_for
from marshmallow import fields
from webargs.flaskparser import use_args

from librium.database.pony.db import *
from librium.views.utilities import MyBoolean

bp = Blueprint("book", __name__, url_prefix="/book")


@bp.route("/<int:id>", methods=["GET", "POST"])
@use_args({
    'title': fields.String(),
    'isbn': fields.String(),
    'format': fields.Integer(),
    'released': fields.Integer(),
    'price': fields.Float(),
    'page_count': fields.Integer(),
    'read': MyBoolean(missing=False),
    'authors': fields.List(fields.Integer()),
    'genres': fields.List(fields.Integer()),
    'publishers': fields.List(fields.Integer()),
    'languages': fields.List(fields.Integer())
})
def index(args, id):
    if request.method == "POST":

        lookup_table = {
            "genres": Genre,
            "publishers": Publisher,
            "authors": Author,
            "languages": Language
        }

        def parse(table, key):
            return table[key]

        book = Book[id]

        for k, v in lookup_table.items():
            args[k] = [v[i] for i in args[k]]
        args["format"] = Format[args["format"]]

        # TODO: Include series

        print(args)

        book.set(**args)
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
