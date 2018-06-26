from math import ceil
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    g,
    has_request_context,
    _request_ctx_stack,
)

from librium.database import Book, Format

bp = Blueprint("book", __name__, url_prefix="/book")


def add_formats(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        formats = Format.query.all()
        g.formats = formats
        return func(*args, **kwargs)

    return decorated_function


@bp.route("/<int:_id>")
@add_formats
def index(_id):
    book = Book.query.filter_by(_id=_id).one()

    return render_template("book/index.html", book=book)
