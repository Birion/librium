"""
Book service for the Librium application.

This module provides a service for interacting with the Book model.
"""

from decimal import Decimal
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
from librium.database.sqlalchemy.db import book_genres, book_publishers
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
            The book if found and not deleted, None otherwise
        """
        try:
            logger.debug(f"Getting book with ID: {book_id}")
            book = Session.get(Book, book_id)
            if book and not book.deleted:
                logger.debug(f"Found book: {book.title} (ID: {book.id})")
                return book
            else:
                if book and book.deleted:
                    logger.info(f"Book with ID {book_id} is marked as deleted")
                else:
                    logger.info(f"Book with ID {book_id} not found")
                return None
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
            The book if found and not deleted, None otherwise
        """
        try:
            logger.debug(f"Getting book with UUID: {uuid}")
            book = (
                Session.scalars(
                    select(Book).where(Book.uuid == uuid, Book.deleted.is_(False))
                )
                .unique()
                .one_or_none()
            )
            if book:
                logger.debug(f"Found book: {book.title} (ID: {book.id})")
                return book
            else:
                logger.info(f"Book with UUID {uuid} not found or is deleted")
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting book with UUID {uuid}: {e}")
            return None

    @staticmethod
    @read_only
    def get_all() -> List[Book]:
        """
        Get all non-deleted books.

        Returns:
            A list of all non-deleted books

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all non-deleted books")
            books = (
                Session.scalars(select(Book).where(Book.deleted.is_(False)))
                .unique()
                .all()
            )
            logger.debug(f"Found {len(books)} non-deleted books")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting all books: {e}")
            raise

    @staticmethod
    @read_only
    def get_paginated(
        page: int = 1,
        page_size: int = 30,
        filter_read: Optional[bool] = None,
        search: Optional[str] = None,
        start_with: Optional[str] = None,
        exact_name: Optional[str] = None,
        sort_by: str = "title",
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

            # Build the base query
            query = select(Book).where(Book.deleted.is_(False))

            # Apply read filter if provided
            if filter_read is not None:
                query = query.where(Book.read.is_(filter_read))

            # Apply search filter if provided
            if search:
                query = query.where(Book.title.ilike(f"%{search}%"))

            # Apply start_with filter if provided
            if start_with:
                query = query.where(Book.title.ilike(f"{start_with}%"))

            # Apply exact_name filter if provided
            if exact_name:
                query = query.where(Book.title == exact_name)

            total_count = len(Session.scalars(query).unique().all())

            # Apply sorting
            if sort_by == "title":
                order_attr = Book.title
            elif sort_by == "released":
                order_attr = Book.released
            elif sort_by == "price":
                order_attr = Book.price
            elif sort_by == "page_count":
                order_attr = Book.page_count
            elif sort_by == "read":
                order_attr = Book.read
            else:
                # Default to title if sort_by is not recognised
                order_attr = Book.title

            logger.debug(f"Sorting by {sort_by} in {sort_order} order")

            # Apply sort order
            if sort_order.lower() == "desc":
                query = query.order_by(order_attr.desc())
            else:
                query = query.order_by(order_attr.asc())

            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

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
    def get_read() -> List[Book]:
        """
        Get all read books that are not deleted.

        Returns:
            A list of all read books that are not deleted

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all read books that are not deleted")
            books = list(Session.query(Book).where(Book.read, Book.deleted.is_(False)))
            logger.debug(f"Found {len(books)} read books that are not deleted")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting read books: {e}")
            raise

    @staticmethod
    @read_only
    def get_unread() -> List[Book]:
        """
        Get all unread books that are not deleted.

        Returns:
            A list of all unread books that are not deleted

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug("Getting all unread books that are not deleted")
            books = Session.scalars(
                select(Book).where(Book.read.is_(False), Book.deleted.is_(False))
            ).all()
            logger.debug(f"Found {len(books)} unread books that are not deleted")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting unread books: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_title(title: str, partial_match: bool = True) -> List[Book]:
        """
        Get books by title.

        Args:
            title: The title to search for
            partial_match: If True, search for partial matches; if False, search for exact matches

        Returns:
            A list of books matching the title criteria that are not deleted

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug(
                f"Getting books by title: {title} (partial_match={partial_match})"
            )
            if partial_match:
                books = (
                    Session.query(Book)
                    .where(Book.title.ilike(f"%{title}%"), Book.deleted.is_(False))
                    .all()
                )
            else:
                books = (
                    Session.query(Book)
                    .where(Book.title == title, Book.deleted.is_(False))
                    .all()
                )
            logger.debug(f"Found {len(books)} books matching title: {title}")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by title {title}: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_author(author_id: int) -> List[Book]:
        """
        Get books by author ID.

        Args:
            author_id: The ID of the author

        Returns:
            A list of non-deleted books by the specified author

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug(f"Getting books by author ID: {author_id}")
            books = (
                Session.query(Book)
                .join(AuthorOrdering, Book.id == AuthorOrdering.book_id)
                .where(AuthorOrdering.author_id == author_id, Book.deleted.is_(False))
                .all()
            )
            logger.debug(f"Found {len(books)} books by author ID: {author_id}")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by author ID {author_id}: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_genre(genre_id: int) -> List[Book]:
        """
        Get books by genre ID.

        Args:
            genre_id: The ID of the genre

        Returns:
            A list of non-deleted books in the specified genre

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug(f"Getting books by genre ID: {genre_id}")
            books = (
                Session.query(Book)
                .join(book_genres, Book.id == book_genres.c.book_id)
                .where(book_genres.c.genre_id == genre_id, Book.deleted.is_(False))
                .all()
            )
            logger.debug(f"Found {len(books)} books by genre ID: {genre_id}")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by genre ID {genre_id}: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_publisher(publisher_id: int) -> List[Book]:
        """
        Get books by publisher ID.

        Args:
            publisher_id: The ID of the publisher

        Returns:
            A list of non-deleted books from the specified publisher

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.debug(f"Getting books by publisher ID: {publisher_id}")
            books = (
                Session.query(Book)
                .join(book_publishers, Book.id == book_publishers.c.book_id)
                .where(
                    book_publishers.c.publisher_id == publisher_id,
                    Book.deleted.is_(False),
                )
                .all()
            )
            logger.debug(f"Found {len(books)} books by publisher ID: {publisher_id}")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by publisher ID {publisher_id}: {e}")
            raise

    @staticmethod
    @read_only
    def get_index_by_series(book_id: int, series_id: int) -> list[Decimal] | None:
        """
        Get the index of a book in a specific series.

        Args:
            book_id: The ID of the book
            series_id: The ID of the series
        Returns:
            The index of the book in the series, or 0.0 if not found
        """
        try:
            logger.debug(
                f"Getting index of book ID {book_id} in series ID {series_id}"
            )
            index = (
                Session.query(SeriesIndex)
                .where(
                    SeriesIndex.book_id == book_id,
                    SeriesIndex.series_id == series_id,
                )
                .all()
            )
            if index is not None:
                index = [x.idx for x in index]
                logger.debug(f"Found index: {index}")
                return index
            else:
                logger.info(
                    f"No index found for book ID {book_id} in series ID {series_id}"
                )
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting index for book ID {book_id}: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_year(
        year: int = None, start_year: int = None, end_year: int = None
    ) -> List[Book]:
        """
        Get books by release year or range of years.

        Args:
            year: Specific release year to search for
            start_year: Start of release year range (inclusive)
            end_year: End of release year range (inclusive)

        Returns:
            A list of non-deleted books matching the year criteria

        Raises:
            ValueError: If invalid year parameters are provided
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            # Validate parameters
            if year is not None and (start_year is not None or end_year is not None):
                raise ValueError("Cannot specify both year and year range")

            if year is None and start_year is None and end_year is None:
                raise ValueError("Must specify either year or year range")

            if year is not None:
                logger.debug(f"Getting books by release year: {year}")
                books = list(
                    Session.query(Book).where(
                        Book.released == year, Book.deleted.is_(False)
                    )
                )
                logger.debug(f"Found {len(books)} books released in {year}")
            else:
                # Handle year range
                query = Session.query(Book).where(Book.deleted.is_(False))

                if start_year is not None:
                    query = query.where(Book.released >= start_year)

                if end_year is not None:
                    query = query.where(Book.released <= end_year)

                range_desc = f"{start_year or 'any'} to {end_year or 'any'}"
                logger.debug(f"Getting books by release year range: {range_desc}")
                books = list(query)
                logger.debug(f"Found {len(books)} books released in range {range_desc}")

            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by year: {e}")
            raise

    @staticmethod
    @read_only
    def get_by_price_range(
        min_price: Decimal = None, max_price: Decimal = None
    ) -> List[Book]:
        """
        Get books within a specific price range.

        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)

        Returns:
            A list of non-deleted books within the specified price range

        Raises:
            ValueError: If invalid price parameters are provided
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            # Validate parameters
            if min_price is None and max_price is None:
                raise ValueError("Must specify at least one of min_price or max_price")

            if min_price is not None and min_price < 0:
                raise ValueError("min_price cannot be negative")

            if max_price is not None and max_price < 0:
                raise ValueError("max_price cannot be negative")

            if (
                min_price is not None
                and max_price is not None
                and min_price > max_price
            ):
                raise ValueError("min_price cannot be greater than max_price")

            # Build query
            query = Session.query(Book).where(Book.deleted.is_(False))

            if min_price is not None:
                query = query.where(Book.price >= min_price)

            if max_price is not None:
                query = query.where(Book.price <= max_price)

            range_desc = f"{min_price or 'any'} to {max_price or 'any'}"
            logger.debug(f"Getting books by price range: {range_desc}")
            books = list(query)
            logger.debug(f"Found {len(books)} books in price range {range_desc}")

            return books
        except SQLAlchemyError as e:
            logger.error(f"Error getting books by price range: {e}")
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
        title = title.strip()
        try:
            logger.info(f"Creating new book: {title}")

            # Get the format
            format_obj = Session.get(Format, format_id)
            if not format_obj:
                logger.error(f"Format with ID {format_id} not found")
                raise ValueError(f"Format with ID {format_id} not found")

            logger.debug(kwargs)

            # Create the book
            book = Book(title=title, format=format_obj)

            # Update the book attributes
            for key, value in kwargs.items():
                setattr(book, key, value.strip() if isinstance(value, str) else value)

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
                setattr(book, key, value.strip() if isinstance(value, str) else value)

            logger.info(f"Book updated: {book.title} (ID: {book.id})")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error updating book with ID {book_id}: {e}")
            raise

    @staticmethod
    @transactional
    def delete(book_id: int) -> bool:
        """
        Soft delete a book by setting its deleted flag to True.

        Args:
            book_id: The ID of the book to delete

        Returns:
            True if the book was soft deleted, False otherwise

        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            logger.info(f"Soft deleting book with ID: {book_id}")

            # Get the book
            book = Session.get(Book, book_id)
            if not book:
                logger.warning(f"Book with ID {book_id} not found for deletion")
                return False

            # Store book title for logging
            book_title = book.title

            # Soft delete the book by setting the deleted flag
            book.deleted = True

            logger.info(f"Book soft deleted: {book_title} (ID: {book_id})")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error soft deleting book with ID {book_id}: {e}")
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
