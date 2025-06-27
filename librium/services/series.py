"""
Series service for the Librium application.

This module provides a service for interacting with the Series model.
"""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from librium.core.logging import logger
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
    def get_paginated(
        page: int = 1,
        page_size: int = 30,
        start_with: Optional[str] = None,
        exact_name: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        **kwargs,
    ) -> tuple[List[Series], int]:
        """
        Get a paginated list of non-deleted genres with optional filtering and sorting.
        Follows the same logic as get_genres().
        """
        try:
            logger.debug(
                f"Getting paginated genres (page={page}, page_size={page_size}, "
                f"start_with={start_with}, exact_name={exact_name})"
            )
            query = select(Series).where(Series.deleted.is_(False))
            count_query = select(Series.id).where(Series.deleted.is_(False))

            # Apply filters as in get_genres()
            if start_with:
                query = query.where(Series.name.ilike(f"{start_with.lower()}%"))
                count_query = count_query.where(
                    Series.name.ilike(f"{start_with.lower()}%")
                )
            if exact_name:
                query = query.where(Series.name == exact_name)
                count_query = count_query.where(Series.name == exact_name)

            total_count = len(Session.scalars(count_query).all())

            # Only 'name' is supported for sorting
            order_attr = Series.name
            logger.debug(f"Sorting by {sort_by} in {sort_order} order")
            if sort_order.lower() == "desc":
                query = query.order_by(order_attr.desc())
            else:
                query = query.order_by(order_attr.asc())

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            genres = Session.scalars(query).unique().all()
            logger.debug(
                f"Found {len(genres)} genres for page {page} (total: {total_count})"
            )
            return genres, total_count
        except SQLAlchemyError as e:
            logger.error(f"Error getting paginated genres: {e}")
            raise

    @staticmethod
    @read_only
    def get_books_in_series(series_id: int) -> List[Book]:
        """
        Get all books in a series.

        Args:
            series_id: The ID of the series

        Returns:
            A list of books in the series
        """
        series = Session.get(Series, series_id)
        if not series:
            return []

        books = (
            Session.query(Book)
            .filter(Book.id.in_([b.book.id for b in series.books]))
            .all()
        )

        return books

    @staticmethod
    @read_only
    def get_books_in_series_formatted(series_id: int) -> List[dict[str, Any]]:
        """
        Get all books in a series formatted for output.

        Args:
            series_id: The ID of the series

        Returns:
            A list of dictionaries containing book information
        """
        books = []
        for book in SeriesService.get_books_in_series(series_id):
            from librium.services import BookService
            series_book = {
                "name": book.name,
                "id": book.id,
                "idx": BookService.get_index_by_series(book.id, series_id),
                "authors": [
                    {"name": a.author.name, "id": a.author.id, "idx": a.idx} for a in book.authors
                ],
                "published": book.released,
                "uuid": book.uuid,
            }
            series_book["authors"].sort(key=lambda x: x["idx"])
            books.append(series_book)
        books.sort(key=lambda x: x["idx"])

        return books