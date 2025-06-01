from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from webargs.flaskparser import use_args, use_kwargs

from librium.services import (
    AuthorService,
    BookService,
    FormatService,
    GenreService,
    LanguageService,
    PublisherService,
    SeriesService,
)
from librium.views.utilities import BookSchema

bp = Blueprint("book", __name__, url_prefix="/book")


@bp.route("/<int:id>", methods=["GET", "POST"])
@use_kwargs(BookSchema, location="form")
def index(id, **kwargs):
    if request.method == "POST":
        # Get the book and update it using the BookService
        book = BookService.get_by_id(id)
        if not book:
            book = BookService.create(
                title=kwargs.get("title"), format_id=kwargs.get("format", 1), **kwargs
            )
        else:
            # Update the book with the provided data
            book = BookService.add_or_update(book, kwargs)
        return jsonify({"url": url_for("book.index", id=id)})
    else:
        # Get the book and related data using services
        book = BookService.get_by_id(id)
        if not book:
            return redirect(url_for("main.index"))

        # Get all the necessary data for the template
        options = {
            "book": book,
            "genres": GenreService.get_all(),
            "formats": FormatService.get_all(),
            "languages": LanguageService.get_all(),
            "publishers": PublisherService.get_all(),
            "series": SeriesService.get_all(),
            "authors": AuthorService.get_all(),
        }
        return render_template("book/index.html", **options)


@bp.route("/add", methods=["GET", "POST"])
@use_args(BookSchema, location="form")
def add(args):
    if request.method == "POST":
        # Create a new book using the BookService
        # First create a book with a temporary title
        book = BookService.create(title="x", format_id=args.get("format", 1))
        # Then update it with all the provided data
        BookService.add_or_update(book, args)
        return jsonify({"url": url_for("book.index", id=book.id)})
    else:
        # Get all the necessary data for the template using services
        options = {
            "genres": GenreService.get_all(),
            "formats": FormatService.get_all(),
            "languages": LanguageService.get_all(),
            "publishers": PublisherService.get_all(),
            "series": SeriesService.get_all(),
            "authors": AuthorService.get_all(),
        }
        return render_template("book/index.html", **options)
