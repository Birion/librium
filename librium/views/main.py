from typing import Tuple, Any

from flask import Blueprint, render_template
from marshmallow import fields
from webargs.flaskparser import use_args

from librium.database.pony.db import Author, Book
from pony.orm import *

bp = Blueprint("main", __name__)


def get_authors(args) -> Tuple[Any, int]:
    page = args.get("page", 1)

    authors = Author.select().order_by(Author.last_name).page(page)
    max_length = int(count(a for a in Author) / 10)
    return authors, max_length


@bp.route("/")
@use_args({
    "page": fields.Integer()
})
def index(args):
    authors, max_length = get_authors(args)
    return render_template("main/index.html", authors=authors, pagination=max_length)
