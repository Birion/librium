"""
Book service for the Librium application.

This module provides a service for interacting with the Book model.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import select

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
        return Session.get(Book, book_id)

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
        return (
            Session.scalars(select(Book).where(Book.uuid == uuid))
            .unique()
            .one_or_none()
        )

    @staticmethod
    @read_only
    def get_all() -> List[Book]:
        """
        Get all books.

        Returns:
            A list of all books
        """
        return list(Session.query(Book))

    @staticmethod
    @read_only
    def get_read() -> List[Book]:
        """
        Get all read books.

        Returns:
            A list of all read books
        """
        return list(Session.query(Book).where(Book.read))

    @staticmethod
    @read_only
    def get_unread() -> List[Book]:
        """
        Get all unread books.

        Returns:
            A list of all unread books
        """
        return list(Session.query(Book).where(Book.read is False))

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
        """
        format_obj = Session.get(Format, format_id)
        if not format_obj:
            raise ValueError(f"Format with ID {format_id} not found")

        book = Book(title=title, format=format_obj, **kwargs)
        Session.add(book)
        return book

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
        """
        book = Session.get(Book, book_id)
        if not book:
            return None

        # Handle special cases for relationships
        if "format_id" in kwargs:
            format_obj = Session.get(Format, kwargs.pop("format_id"))
            if not format_obj:
                raise ValueError(f"Format with ID {kwargs['format_id']} not found")
            kwargs["format"] = format_obj

        # Update the book attributes
        for key, value in kwargs.items():
            setattr(book, key, value)

        return book

    @staticmethod
    @transactional
    def delete(book_id: int) -> bool:
        """
        Delete a book.

        Args:
            book_id: The ID of the book to delete

        Returns:
            True if the book was deleted, False otherwise
        """
        book = Session.get(Book, book_id)
        if not book:
            return False

        Session.delete(book)
        return True

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
        """

        lookup = ["genres", "publishers", "languages"]

        book.authors = []
        book.series = []

        for key in lookup:
            if table := data.get(key):
                match key:
                    case "genres":
                        data[key] = [GenreService.get_by_id(g) for g in table]
                    case "publishers":
                        data[key] = [PublisherService.get_by_id(g) for g in table]
                    case "languages":
                        data[key] = [LanguageService.get_by_id(g) for g in table]

        data["format"] = FormatService.get_by_id(data["format"])

        for series in book.series:
            Session.delete(series)

        _series = []
        for s in data["series"]:
            si = SeriesIndex(
                book=book, series=SeriesService.get_by_id(s["series"]), idx=s["idx"]
            )
            Session.add(si)
            _series.append(si)

        _authors = []

        for author_order in book.authors:
            Session.delete(author_order)

        i = 1
        try:
            for a in data.get("authors"):
                ax = AuthorOrdering(book=book, author=AuthorService.get_by_id(a), idx=i)
                Session.add(ax)
                i += 1
                _authors.append(ax)
        except TypeError:
            pass

        data["series"] = _series
        data["authors"] = _authors

        book.set(**data)
        return book
