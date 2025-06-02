"""
Series service for the Librium application.

This module provides a service for interacting with the Series model.
"""

from typing import List, Optional

from sqlalchemy import select

from librium.database import (
    Book,
    Series,
    SeriesIndex,
    Session,
    read_only,
    transactional,
)


class SeriesService:
    """Service for interacting with the Series model."""

    @staticmethod
    @read_only
    def get_by_id(series_id: int) -> Optional[Series]:
        """
        Get a series by its ID.

        Args:
            series_id: The ID of the series

        Returns:
            The series if found, None otherwise
        """
        return Session.get(Series, series_id)

    @staticmethod
    @read_only
    def get_all() -> List[Series]:
        """
        Get all series.

        Returns:
            A list of all series
        """
        return Session.query(Series).order_by(Series.name).all()

    @staticmethod
    @transactional
    def create(name: str, **kwargs) -> Series:
        """
        Create a new series.

        Args:
            name: The name of the series
            **kwargs: Additional series attributes

        Returns:
            The created series
        """
        series = Series(name=name, **kwargs)
        Session.add(series)
        return series

    @staticmethod
    @transactional
    def update(series_id: int, **kwargs) -> Optional[Series]:
        """
        Update a series.

        Args:
            series_id: The ID of the series to update
            **kwargs: The attributes to update

        Returns:
            The updated series if found, None otherwise
        """
        series = Session.get(Series, series_id)
        if not series:
            return None

        # Update the series attributes
        for key, value in kwargs.items():
            setattr(series, key, value)

        return series

    @staticmethod
    @transactional
    def delete(series_id: int) -> bool:
        """
        Delete a series.

        Args:
            series_id: The ID of the series to delete

        Returns:
            True if the series was deleted, False otherwise
        """
        series = Session.get(Series, series_id)
        if not series:
            return False

        series.delete()
        return True

    @staticmethod
    @transactional
    def add_book_to_series(
        book_id: int, series_id: int, index: float
    ) -> Optional[SeriesIndex]:
        """
        Add a book to a series with the specified index.

        Args:
            book_id: The ID of the book to add
            series_id: The ID of the series to add the book to
            index: The index of the book in the series

        Returns:
            The created SeriesIndex if successful, None otherwise
        """
        book = Session.get(Book, book_id)
        series = Session.get(Series, series_id)

        if not book or not series:
            return None

        # Check if the book is already in the series
        existing = Session.get(SeriesIndex, {"book": book, "series": series})
        if existing:
            existing.idx = index
            return existing

        # Add the book to the series
        series_index = Session.get(
            SeriesIndex, {"idx": index, "book": book, "series": series}
        )
        return series_index

    @staticmethod
    @transactional
    def remove_book_from_series(book_id: int, series_id: int) -> bool:
        """
        Remove a book from a series.

        Args:
            book_id: The ID of the book to remove
            series_id: The ID of the series to remove the book from

        Returns:
            True if the book was removed, False otherwise
        """
        book = Session.get(Book, book_id)
        series = Session.get(Series, series_id)

        if not book or not series:
            return False

        series_index = Session.get(SeriesIndex, {"book": book, "series": series})
        if not series_index:
            return False

        series_index.delete()
        return True

    @staticmethod
    @read_only
    def get_books_in_series(series_id: int) -> List[Book]:
        """
        Get all books in a series, ordered by their index.

        Args:
            series_id: The ID of the series

        Returns:
            A list of books in the series, ordered by their index
        """
        series = Session.get(Series, series_id)
        if not series:
            return []

        books = (
            Session.query(Book)
            .filter(Book.id.in_([b.book.id for b in series.books]))
            # .order_by(SeriesIndex.idx)
            .all()
        )

        return books
