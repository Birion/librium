from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
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
from librium.core.logging import get_logger

# Get logger for this module
logger = get_logger("views.book")

bp = Blueprint("book", __name__, url_prefix="/book")


@bp.route("/<int:id>", methods=["GET", "POST"])
@use_kwargs(BookSchema, location="form")
def index(id, **kwargs):
    logger.info(f"Book index view for ID: {id}, method: {request.method}")

    try:
        if request.method == "POST":
            logger.debug(f"POST request for book ID: {id} with data: {kwargs}")

            # Get the book and update it using the BookService
            book = BookService.get_by_id(id)
            if not book:
                logger.info(f"Book with ID {id} not found, creating new book")
                book = BookService.create(
                    title=kwargs.get("title"),
                    format_id=kwargs.get("format", 1),
                    **kwargs,
                )
                logger.info(f"Created new book with ID: {book.id}")
            else:
                logger.info(f"Updating book: {book.title} (ID: {book.id})")
                # Update the book with the provided data
                book = BookService.add_or_update(book, kwargs)
                logger.info(f"Book updated: {book.title} (ID: {book.id})")

            return jsonify({"url": url_for("book.index", id=id)})
        else:
            # Get the book and related data using services
            logger.debug(f"GET request for book ID: {id}")
            book = BookService.get_by_id(id)
            if not book:
                logger.warning(f"Book with ID {id} not found, redirecting to main page")
                return redirect(url_for("main.index"))

            logger.debug(f"Found book: {book.title} (ID: {book.id})")

            # Get all the necessary data for the template
            try:
                options = {
                    "book": book,
                    "genres": GenreService.get_all(),
                    "formats": FormatService.get_all(),
                    "languages": LanguageService.get_all(),
                    "publishers": PublisherService.get_all(),
                    "series": SeriesService.get_all(),
                    "authors": AuthorService.get_all(),
                }
                logger.debug(
                    "Successfully retrieved all related data for book template"
                )
                return render_template("book/index.html", **options)
            except SQLAlchemyError as e:
                logger.error(f"Error retrieving related data for book {id}: {e}")
                # Still show the book page, but with a message about the error
                return render_template(
                    "book/index.html",
                    book=book,
                    error_message="Some data could not be loaded.",
                )
    except ValueError as e:
        logger.error(f"Value error in book index view for ID {id}: {e}")
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in book index view for ID {id}: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in book index view for ID {id}: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route("/add", methods=["GET", "POST"])
@use_args(BookSchema, location="form")
def add(args):
    logger.info(f"Book add view, method: {request.method}")

    try:
        if request.method == "POST":
            logger.debug(f"POST request to add book with data: {args}")

            # Create a new book using the BookService
            # First create a book with a temporary title
            logger.debug("Creating book with temporary title")
            book = BookService.create(title="x", format_id=args.get("format", 1))
            logger.info(f"Created book with temporary title, ID: {book.id}")

            # Then update it with all the provided data
            logger.debug(f"Updating book with provided data")
            BookService.add_or_update(book, args)
            logger.info(f"Book created and updated: {book.title} (ID: {book.id})")

            return jsonify({"url": url_for("book.index", id=book.id)})
        else:
            logger.debug("GET request to add book form")

            # Get all the necessary data for the template using services
            try:
                options = {
                    "genres": GenreService.get_all(),
                    "formats": FormatService.get_all(),
                    "languages": LanguageService.get_all(),
                    "publishers": PublisherService.get_all(),
                    "series": SeriesService.get_all(),
                    "authors": AuthorService.get_all(),
                }
                logger.debug("Successfully retrieved all data for add book form")
                return render_template("book/index.html", **options)
            except SQLAlchemyError as e:
                logger.error(f"Error retrieving data for add book form: {e}")
                # Show the form with an error message
                return render_template(
                    "book/index.html", error_message="Some data could not be loaded."
                )
    except ValueError as e:
        logger.error(f"Value error in book add view: {e}")
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in book add view: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in book add view: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
