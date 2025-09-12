"""
Genre service for the Librium application.

This module provides a service for interacting with the Genre model.
"""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from librium.core.logging import get_logger
from librium.database import Book, Genre, Session, transactional, read_only

# Get logger for this module
logger = get_logger("services.genre")


class GenreService:
    """Service for interacting with the Genre model."""

    @staticmethod
    @read_only
    def get_by_id(genre_id: int) -> Optional[Genre]:
        """
        Get a genre by its ID.

        Args:
            genre_id: The ID of the genre

        Returns:
            The genre if found and not deleted, None otherwise
        """
        genre = Session.get(Genre, genre_id)
        if genre and not genre.deleted:
            return genre
        return None

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Genre]:
        """
        Get a genre by its name.

        Args:
            name: The name of the genre

        Returns:
            The genre if found and not deleted, None otherwise
        """
        return (
            Session.query(Genre)
            .where(Genre.name == name, Genre.deleted == False)
            .one_or_none()
        )

    @staticmethod
    @read_only
    def get_all() -> List[Genre]:
        """
        Get all genres that are not deleted.

        Returns:
            A list of all genres that are not deleted
        """
        return (
            Session.query(Genre)
            .filter(Genre.deleted == False)
            .order_by(Genre.name)
            .all()
        )

    @staticmethod
    @transactional
    def create(name: str) -> Genre:
        """
        Create a new genre.

        Args:
            name: The name of the genre

        Returns:
            The created genre
        """
        if not name or not name.strip():
            raise ValueError("Genre name cannot be empty")

        if len(name) > 50:
            raise ValueError("Genre name cannot be longer than 50 characters")

        genre_obj = Genre(name=name)
        Session.add(genre_obj)
        return genre_obj

    @staticmethod
    @transactional
    def update(genre_id: int, name: str) -> Optional[Genre]:
        """
        Update a genre.

        Args:
            genre_id: The ID of the genre to update
            name: The new name of the genre

        Returns:
            The updated genre if found, None otherwise
        """
        genre_obj = Session.get(Genre, genre_id)
        if not genre_obj:
            return None

        if not name or not name.strip():
            raise ValueError("Genre name cannot be empty")

        if len(name) > 50:
            raise ValueError("Genre name cannot be longer than 50 characters")

        genre_obj.name = name
        return genre_obj

    @staticmethod
    @transactional
    def delete(genre_id: int) -> bool:
        """
        Soft delete a genre by setting its deleted flag to True.

        Args:
            genre_id: The ID of the genre to delete

        Returns:
            True if the genre was soft deleted, False otherwise
        """
        genre_obj = Session.get(Genre, genre_id)
        if not genre_obj:
            return False

        genre_obj.deleted = True
        return True

    @staticmethod
    @read_only
    def get_paginated(
        page: int = 1,
        page_size: int = 30,
        filter_read: Optional[bool] = None,
        search: Optional[str] = None,
        start_with: Optional[str] = None,
        ends_with: Optional[str] = None,
        exact_name: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        **kwargs,
    ) -> tuple[List[Genre], int]:
        """
        Get a paginated list of non-deleted genres with optional filtering and sorting.
        Follows the same logic as get_genres().
        """
        try:
            logger.debug(
                f"Getting paginated genres (page={page}, page_size={page_size}, "
                f"search={search}, start_with={start_with}, ends_with={ends_with}, exact_name={exact_name})"
            )
            query = select(Genre).where(Genre.deleted.is_(False))

            # Apply filters as in get_genres()
            if search:
                query = query.where(Genre.name.ilike(f"%{search}%"))
            if start_with:
                query = query.where(Genre.name.ilike(f"{start_with.lower()}%"))
            if ends_with:
                query = query.where(Genre.name.ilike(f"%{ends_with}"))
            if exact_name:
                query = query.where(Genre.name == exact_name)
            if filter_read is not None:
                query = query.join(Genre.books).where(Book.read.is_(filter_read))

            total_count = len(Session.scalars(query).unique().all())

            # Only 'name' is supported for sorting
            order_attr = Genre.name
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
    def get_books_in_genre(genre_id: int, read: Optional[bool]) -> List[Book]:
        """
        Get all books associated with a genre.

        Args:
            genre_id: The ID of the genre
            read: Optional filter for read status of books

        Returns:
            A list of books associated with the genre
        """
        logger.debug(f"Getting books for genre ID: {genre_id}")
        genre = Session.get(Genre, genre_id)
        if not genre or genre.deleted:
            logger.debug(f"Genre with ID {genre_id} not found or is deleted")
            return []

        # Build base selector for books in this genre, excluding deleted
        selector = (
            select(Book)
            .where(Book.genres.contains(genre))
            .where(Book.deleted.is_(False))
        )
        # Apply read filter only if explicitly provided
        if read is not None:
            selector = selector.where(Book.read.is_(read))

        books = Session.scalars(selector).unique().all()
        logger.debug(f"Found {len(books)} books in genre {genre.name} (ID: {genre_id})")

        return books

    @staticmethod
    @read_only
    def get_books_in_genre_formatted(
        genre_id: int, read: Optional[bool]
    ) -> List[dict[str, Any]]:
        """
        Get all books associated with a genre.

        Args:
            genre_id: The ID of the genre
            read: Optional filter for read status of books

        Returns:
            A list of books associated with the genre
        """
        books = []
        for book in GenreService.get_books_in_genre(genre_id, read):
            book_info = {
                "name": book.title,
                "id": book.id,
                "uuid": book.uuid,
                "authors": [],
                "series": [],
                "released": book.released,
            }
            for s in book.series:
                book_info["series"].append(
                    {"name": s.series.name, "id": s.series.id, "idx": s.idx}
                )
            for a in book.authors:
                book_info["authors"].append(
                    {"name": a.author.name, "id": a.author.id, "idx": a.idx}
                )
            book_info["authors"].sort(key=lambda x: x["idx"])
            books.append(book_info)
        try:
            books.sort(
                key=lambda x: (
                    x["series"][0]["name"] if x.get("series") else "",
                    x["series"][0]["idx"] if x.get("series") else 0,
                    x["name"],
                )
            )
        except IndexError:
            books.sort(key=lambda x: x["name"])

        return books
