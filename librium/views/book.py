from functools import wraps

from flask import Blueprint, render_template, g

from librium.database import Book, Format, Author, Series, Genre, Publisher

bp = Blueprint("book", __name__, url_prefix="/book")


def add_formats(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        g.formats = Format.query.all()
        g.authors = Author.query.order_by(Author.last_name).all()
        g.genres = Genre.query.order_by(Genre.name).all()
        g.series = Series.query.order_by(Series.name).all()
        g.publishers = Publisher.query.order_by(Publisher.name).all()
        return func(*args, **kwargs)

    return decorated_function


@bp.route("/<int:_id>")
@add_formats
def index(_id):
    book = Book.query.filter_by(_id=_id).one()

    return render_template("book/index.html", book=book)
