from math import ceil

from flask import (
    Blueprint,
    render_template,
    request,
    has_request_context,
    _request_ctx_stack,
    session,
    url_for,
)

from librium.database import Book

bp = Blueprint("main", __name__)


def get_books(filters: list, order, offset: int = 0, count: int = 20):
    books = Book.query
    page = offset + 1
    span = 4
    if has_request_context():
        ctx = _request_ctx_stack.top
        if ctx:
            ctx.g.page = page
            ctx.g.count = int(ceil(books.count() / count))
            ctx.g.pages = [
                x + 1
                for x in range(ctx.g.count)
                if x + 1 == 1
                or x + 1 == ctx.g.count
                or x in range(page - span, page + span)
            ]
    for f in filters:
        books.filter_by(f)
    books.order_by(order)
    return books[count * offset : count * page]


@bp.route("/")
def index():
    page = request.args.get("page", "1")
    count = request.args.get("count", "20")
    offset = int(page) - 1
    count = int(count)
    books = get_books(filters=[], order=Book.title, offset=offset, count=count)
    session["next"] = url_for("main.index", page=request.args.get("page", 1))
    return render_template("main/index.html", books=books)
