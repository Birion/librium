"""
Year service for the Librium application.

This module provides a service for interacting with the Book model by year released.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from librium.core.logging import get_logger
from librium.database import Book, Session, read_only

# Get logger for this module
logger = get_logger("services.year")


class YearService:
    """Service for interacting with the Book model by years."""

    @staticmethod
    @read_only
    def get_paginated(
        page: int = 1,
        page_size: int = 5,
        filter_read: Optional[bool] = None,
        search: Optional[str] = None,
        start_with: Optional[str] = None,
        exact_name: Optional[str] = None,
        sort_by: str = "released",
        sort_order: str = "asc",
    ) -> tuple[List[Book], int]:
        """
        Get a paginated list of non-deleted books with optional filtering and sorting.

        Args:
            page: The page number (1-indexed)
            page_size: The number of items per page
            filter_read: If provided, filter books by read status
            search: If provided, filter books by title containing this string
            start_with: If provided, filter books by title starting with this string
            exact_name: If provided, filter books by exact title match
            sort_by: Field to sort by (title, released, price, page_count, read)
            sort_order: Sort order (asc or desc)

        Returns:
            A tuple containing:
                - A list of books for the requested page
                - The total number of books matching the criteria

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug(
                f"Getting paginated books (page={page}, page_size={page_size}, "
                f"filter_read={filter_read}, search={search}, start_with={start_with}, "
                f"exact_name={exact_name})"
            )

            offset = (page - 1) * page_size
            years = [year[0] for year in Session.query(Book.released).order_by(Book.released).distinct().offset(offset).limit(page_size).all()]

            # Build the base query
            query = select(Book).where(Book.deleted.is_(False)).where(Book.released.in_(years))

            total_count = len(Session.scalars(query).unique().all())

            # Apply sorting
            order_attr = Book.title

            logger.debug(f"Sorting by {sort_by} in {sort_order} order")

            # Apply sort order
            if sort_order.lower() == "desc":
                query = query.order_by(order_attr.desc())
            else:
                query = query.order_by(order_attr.asc())

            # Execute query
            books = Session.scalars(query).unique().all()

            logger.debug(
                f"Found {len(books)} books for page {page} (total: {total_count})"
            )
            return books, total_count
        except SQLAlchemyError as e:
            logger.error(f"Error getting paginated books: {e}")
            raise

    @staticmethod
    @read_only
    def get_books_in_year(year: int) -> List[Book]:
        """
        Get all books published in a specific year.

        Args:
            year: The year published

        Returns:
            A list of books published in the specified year
        """
        from librium.services import BookService
        logger.debug(f"Getting books for year: {year}")
        year_books = BookService.get_by_year(year)
        if not year_books:
            logger.debug(f"No books found for year: {year}")
            return []

        books = [book for book in year_books if not book.deleted]
        books.sort(key=lambda x: x.title)
        logger.debug(f"Found {len(books)} books published in {year}")

        return books

    @staticmethod
    @read_only
    def get_books_in_year_formatted(year: int) -> List[Book]:
        """
        Get all books published in a specific year.

        Args:
            year: The year published

        Returns:
            A list of books published in the specified year
        """
        return YearService.get_books_in_year(year)
