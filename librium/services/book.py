"""
Book service for the Librium application.

This module provides a service for interacting with the Book model.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from librium.database import (
    AuthorOrdering,
    Book,
    Format,
    SeriesIndex,
    Session,
    read_only,
    transactional,
)
from librium.services.author import AuthorService
from librium.services.format import FormatService
from librium.services.genre import GenreService
from librium.services.language import LanguageService
from librium.services.publisher import PublisherService
from librium.services.series import SeriesService
from librium.core.logging import get_logger

# Get logger for this module
logger = get_logger("services.book")


class BookService:
    """Service for interacting with the Book model."""

    @staticmethod
    @read_only
    def get_by_id(book_id: int) -> Optional[Book]:
        """
        Get a book by its ID.

        Args:
            book_id: The ID of the book

        Returns:
            The book if found, None otherwise
        """
        try:
            logger.debug(f"Getting book with ID: {book_id}")
            book = Session.get(Book, book_id)
            if book:
                logger.debug(f"Found book: {book.title} (ID: {book.id})")
            else:
                logger.info(f"Book with ID {book_id} not found")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error getting book with ID {book_id}: {e}")
            return None

    @staticmethod
    @read_only
    def get_by_uuid(uuid: str) -> Optional[Book]:
        """
        Get a book by its UUID.

        Args:
            uuid: The UUID of the book

        Returns:
            The book if found, None otherwise
        """
        try:
            logger.debug(f"Getting book with UUID: {uuid}")
            book = (
                Session.scalars(select(Book).where(Book.uuid == uuid))
                .unique()
                .one_or_none()
            )
            if book:
                logger.debug(f"Found book: {book.title} (ID: {book.id})")
            else:
                logger.info(f"Book with UUID {uuid} not found")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error getting book with UUID {uuid}: {e}")
            return None

    @staticmethod
    @read_only
    def get_all() -> List[Book]:
        """
        Get all books.

        Returns:
            A list of all books

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all books")
            books = list(Session.query(Book))
            logger.debug(f"Found {len(books)} books")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting all books: {e}")
            raise

    @staticmethod
    @read_only
    def get_read() -> List[Book]:
        """
        Get all read books.

        Returns:
            A list of all read books

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all read books")
            books = list(Session.query(Book).where(Book.read))
            logger.debug(f"Found {len(books)} read books")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting read books: {e}")
            raise

    @staticmethod
    @read_only
    def get_unread() -> List[Book]:
        """
        Get all unread books.

        Returns:
            A list of all unread books

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all unread books")
            books = list(Session.query(Book).where(Book.read.is_(False)))
            logger.debug(f"Found {len(books)} unread books")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting unread books: {e}")
            raise

    @staticmethod
    @transactional
    def create(title: str, format_id: int, **kwargs) -> Book:
        """
        Create a new book.

        Args:
            title: The title of the book
            format_id: The ID of the book format
            **kwargs: Additional book attributes

        Returns:
            The created book

        Raises:
            ValueError: If the format with the given ID is not found
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.info(f"Creating new book: {title}")

            # Get the format
            format_obj = Session.get(Format, format_id)
            if not format_obj:
                logger.error(f"Format with ID {format_id} not found")
                raise ValueError(f"Format with ID {format_id} not found")

            # Create the book
            book = Book(title=title, format=format_obj, **kwargs)
            Session.add(book)

            logger.info(f"Book created: {title} (ID: {book.id})")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error creating book {title}: {e}")
            raise

    @staticmethod
    @transactional
    def update(book_id: int, **kwargs) -> Optional[Book]:
        """
        Update a book.

        Args:
            book_id: The ID of the book to update
            **kwargs: The attributes to update

        Returns:
            The updated book if found, None otherwise

        Raises:
            ValueError: If the format with the given ID is not found
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.info(f"Updating book with ID: {book_id}")

            # Get the book
            book = Session.get(Book, book_id)
            if not book:
                logger.warning(f"Book with ID {book_id} not found for update")
                return None

            # Handle special cases for relationships
            if "format_id" in kwargs:
                format_id = kwargs.pop("format_id")
                format_obj = Session.get(Format, format_id)
                if not format_obj:
                    logger.error(f"Format with ID {format_id} not found")
                    raise ValueError(f"Format with ID {format_id} not found")
                kwargs["format"] = format_obj

            # Update the book attributes
            for key, value in kwargs.items():
                setattr(book, key, value)

            logger.info(f"Book updated: {book.title} (ID: {book.id})")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error updating book with ID {book_id}: {e}")
            raise

    @staticmethod
    @transactional
    def delete(book_id: int) -> bool:
        """
        Delete a book.

        Args:
            book_id: The ID of the book to delete

        Returns:
            True if the book was deleted, False otherwise

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.info(f"Deleting book with ID: {book_id}")

            # Get the book
            book = Session.get(Book, book_id)
            if not book:
                logger.warning(f"Book with ID {book_id} not found for deletion")
                return False

            # Store book title for logging
            book_title = book.title

            # Delete the book
            Session.delete(book)

            logger.info(f"Book deleted: {book_title} (ID: {book_id})")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting book with ID {book_id}: {e}")
            raise

    @staticmethod
    @transactional
    def add_or_update(book: Book, data: Dict[str, Any]) -> Book:
        """
        Add or update a book with the given data.

        This method handles the complex logic of updating a book's relationships
        (authors, series, genres, publishers, languages).

        Args:
            book: The book to update
            data: The data to update the book with

        Returns:
            The updated book

        Raises:
            SQLAlchemyError: If there's an error during database operations
            ValueError: If required data is missing or invalid
        """
        try:
            logger.info(f"Adding or updating book: {book.title} (ID: {book.id})")

            lookup = ["genres", "publishers", "languages"]

            # Clear existing relationships
            logger.debug("Clearing existing relationships")
            book.authors = []
            book.series = []

            # Process related entities
            for key in lookup:
                if table := data.get(key):
                    logger.debug(f"Processing {key}: {table}")
                    match key:
                        case "genres":
                            data[key] = [GenreService.get_by_id(g) for g in table]
                        case "publishers":
                            data[key] = [PublisherService.get_by_id(g) for g in table]
                        case "languages":
                            data[key] = [LanguageService.get_by_id(g) for g in table]

            # Get format
            if "format" not in data:
                logger.error("Format is required but not provided")
                raise ValueError("Format is required")

            logger.debug(f"Getting format: {data['format']}")
            data["format"] = FormatService.get_by_id(data["format"])
            if not data["format"]:
                logger.error(f"Format with ID {data['format']} not found")
                raise ValueError(f"Format with ID {data['format']} not found")

            # Process series
            logger.debug("Processing series")
            for series in book.series:
                Session.delete(series)

            _series = []
            if "series" in data:
                for s in data["series"]:
                    series = SeriesService.get_by_id(s["series"])
                    if not series:
                        logger.warning(
                            f"Series with ID {s['series']} not found, skipping"
                        )
                        continue

                    si = SeriesIndex(book=book, series=series, idx=s["idx"])
                    Session.add(si)
                    _series.append(si)

            # Process authors
            logger.debug("Processing authors")
            _authors = []

            for author_order in book.authors:
                Session.delete(author_order)

            i = 1
            try:
                if "authors" in data:
                    for a in data.get("authors"):
                        author = AuthorService.get_by_id(a)
                        if not author:
                            logger.warning(f"Author with ID {a} not found, skipping")
                            continue

                        ax = AuthorOrdering(book=book, author=author, idx=i)
                        Session.add(ax)
                        i += 1
                        _authors.append(ax)
            except TypeError as e:
                logger.error(f"Error processing authors: {e}")
                # Don't re-raise, as this is handled gracefully in the original code

            # Update data with processed relationships
            data["series"] = _series
            data["authors"] = _authors

            # Update the book
            logger.debug(f"Updating book attributes: {data.keys()}")
            book.set(**data)

            logger.info(f"Book updated: {book.title} (ID: {book.id})")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Database error updating book {book.id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating book {book.id}: {e}")
            raise
