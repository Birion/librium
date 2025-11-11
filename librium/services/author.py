"""
Author service for the Librium application.

This module provides a service for interacting with the Author model.
"""

from typing import List, Optional, Any

from sqlalchemy import select

from librium.database import Author, Session, read_only, transactional
from librium.services.series import SeriesService


class AuthorService:
    """Service for interacting with the Author model."""

    @staticmethod
    @read_only
    def get_by_id(author_id: int) -> Optional[Author]:
        """
        Get an author by their ID.

        Args:
            author_id: The ID of the author

        Returns:
            The author if found and not deleted, None otherwise
        """
        author = Session.get(Author, author_id)
        if author and not author.deleted:
            return author
        return None

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Author]:
        """
        Get an author by their name.

        Args:
            name: The name of the author

        Returns:
            The author if found and not deleted, None otherwise
        """
        author = Session.scalar(
            select(Author).where(Author.name == name, Author.deleted == False)
        )
        return author

    @staticmethod
    @read_only
    def get_all() -> List[Author]:
        """
        Get all authors that are not deleted.

        Returns:
            A list of all authors that are not deleted
        """
        return list(Session.query(Author).filter(Author.deleted == False))

    @staticmethod
    @read_only
    def get_by_full_name(
        first_name: Optional[str],
        middle_name: Optional[str],
        last_name: Optional[str],
        prefix: Optional[str],
        suffix: Optional[str],
    ) -> Optional[Author]:
        """
        Get an author by their full name.

        Args:
            first_name: The first name of the author
            middle_name: The middle name of the author
            last_name: The last name of the author
            prefix: The prefix of the author
            suffix: The suffix of the author

        Returns:
            The author if found and not deleted, None otherwise

        Raises:
            ValueError: If neither first_name nor last_name is provided
        """
        if not (first_name or last_name):
            raise ValueError("At least one of first_name or last_name must be provided")
        prefix = prefix or None
        suffix = suffix or None
        selector = (
            select(Author)
            .where(Author.first_name == first_name)
            .where(Author.last_name == last_name)
            .where(Author.middle_name == middle_name)
            .where(Author.prefix == prefix)
            .where(Author.suffix == suffix)
            .where(Author.deleted == False)
        )

        return Session.scalars(selector).unique().one_or_none()

    @staticmethod
    @read_only
    def get_by_last_name_prefix(prefix: str) -> List[Author]:
        """
        Get authors by the prefix of their last name.

        Args:
            prefix: The prefix of the last name

        Returns:
            A list of non-deleted authors with last names starting with the prefix
        """
        selector = (
            select(Author)
            .where(Author.last_name is not None)
            .where(Author.last_name.istartswith(prefix))
            .where(Author.deleted == False)
        )
        return Session.scalars(selector).unique().all()

    @staticmethod
    @transactional
    def create(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Author:
        """
        Create a new author.

        Args:
            first_name: The first name of the author
            last_name: The last name of the author
            name: The full name of the author
            **kwargs: Additional author attributes

        Returns:
            The created author
        """
        if not (first_name or last_name or name):
            raise ValueError(
                "At least one of first_name, last_name, or name must be provided"
            )

        author = Author(first_name=first_name, last_name=last_name, name=name, **kwargs)
        Session.add(author)
        return author

    @staticmethod
    @transactional
    def create_by_name(name: str, **kwargs) -> Author:
        """
        Create a new author.

        Args:
            name: The full name of the author
            **kwargs: Additional author attributes

        Returns:
            The created author
        """

        split_name = name.split(" ")
        options = {
            "first_name": None,
            "last_name": None,
            "middle_name": None,
            "name": name,
        }

        match len(split_name):
            case 1:
                options["last_name"] = split_name[0]
            case 2:
                options["first_name"] = split_name[0]
                options["last_name"] = split_name[1]
            case 3:
                options["first_name"] = split_name[0]
                options["middle_name"] = split_name[1]
                options["last_name"] = split_name[2]

        author = Author(**options)
        Session.add(author)
        return author

    @staticmethod
    @transactional
    def update(author_id: int, **kwargs) -> Optional[Author]:
        """
        Update an author.

        Args:
            author_id: The ID of the author to update
            **kwargs: The attributes to update

        Returns:
            The updated author if found, None otherwise
        """
        author = Session.get(Author, author_id)
        if not author:
            return None

        # Update the author attributes
        for key, value in kwargs.items():
            setattr(author, key, value)

        return author

    @staticmethod
    @transactional
    def delete(author_id: int) -> bool:
        """
        Soft delete an author by setting its deleted flag to True.

        Args:
            author_id: The ID of the author to delete

        Returns:
            True if the author was soft deleted, False otherwise
        """
        author = Session.get(Author, author_id)
        if not author:
            return False

        author.deleted = True
        return True

    # ---------- Formatting helpers moved from view to the service ----------
    @staticmethod
    def _add_book(book: Any, index: int) -> dict:
        return {
            "book": book.title,
            "id": book.id,
            "year": book.released,
            "read": book.read,
            "idx": index,
            "uuid": book.uuid,
        }

    @staticmethod
    def _count_read_for_series(author: Any, series_name: str) -> int:
        series_list = [s for s in SeriesService.get_all() if s.name == series_name]
        series = series_list[0] if series_list else None
        if series:
            books_in_series = SeriesService.get_books_in_series(series.id, None)
            books = [
                b
                for b in books_in_series
                if b.read and any(a.author_id == author.id for a in b.authors)
            ]
        else:
            books = [b.book for b in author.books if b.book.read and not b.book.series]
        return len(books)

    @staticmethod
    def _count_unread_for_series(author: Any, series_name: str) -> int:
        series_list = [s for s in SeriesService.get_all() if s.name == series_name]
        series = series_list[0] if series_list else None
        if series:
            books_in_series = SeriesService.get_books_in_series(series.id, None)
            books = [
                b
                for b in books_in_series
                if (not b.read) and any(a.author_id == author.id for a in b.authors)
            ]
        else:
            books = [
                b.book for b in author.books if (not b.book.read) and not b.book.series
            ]
        return len(books)

    @staticmethod
    def _author_series_entry(series_name: str, books: list, author: Any) -> dict:
        return {
            "series": series_name,
            "status": {
                "read": AuthorService._count_read_for_series(author, series_name),
                "unread": AuthorService._count_unread_for_series(author, series_name),
            },
            "books": books,
        }

    @staticmethod
    def format_authors(authors: List[Any]) -> List[dict]:
        """
        Format authors into the structure expected by the view/template.
        This preserves existing functionality while moving logic into the service.
        """
        formatted: List[dict] = []
        for author in authors:
            authors_series: dict[str, list] = {"0": []}

            # Collect series names for this author's books
            series_names = set()
            for book_author in author.books:
                book = book_author.book
                for series_index in getattr(book, "series", []) or []:
                    # series_index.series.name might be used multiple times; set makes unique
                    series_names.add(series_index.series.name)

            # Initialize keys for each series name
            for name in series_names:
                authors_series[name] = []

            # Add each book to appropriate bucket
            for book_author in author.books:
                book = book_author.book
                if not getattr(book, "series", None):
                    authors_series["0"].append(AuthorService._add_book(book, -1))
                else:
                    for series_index in book.series:
                        authors_series[series_index.series.name].append(
                            AuthorService._add_book(book, series_index.idx)
                        )

            # remove empty standalone bucket
            if not authors_series["0"]:
                del authors_series["0"]

            # sort books inside each series by idx then title
            for sname in list(authors_series.keys()):
                authors_series[sname].sort(key=lambda x: x["book"])
                authors_series[sname].sort(key=lambda x: x["idx"])

            author_data = {
                "author": author.name,
                "series": [
                    AuthorService._author_series_entry(s, authors_series[s], author)
                    for s in authors_series
                ],
                "books": author.books,
            }
            author_data["series"].sort(key=lambda x: x["series"])
            formatted.append(author_data)

        return formatted

    @staticmethod
    @read_only
    def get_authors_with_books() -> List[Author]:
        """
        Get all non-deleted authors who have books.

        Returns:
            A list of non-deleted authors who have books
        """
        return list(
            Session.query(Author)
            .where(Author.books.is_empty() == False, Author.deleted == False)
            .order_by(Author.last_name)
        )

    @staticmethod
    @read_only
    def get_authors_with_read_books(is_read: bool = True) -> List[Author]:
        """
        Get all non-deleted authors who have books with the specified read status.

        Args:
            is_read: Whether to get authors with read or unread books

        Returns:
            A list of non-deleted authors who have books with the specified read status
        """
        return list(
            Session.query(Author).where(
                Author.books.is_empty() == False,
                Author.books.any(lambda b: b.book.read is is_read),
                Author.deleted == False,
            )
        )

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
        sort_by: str = "last_name",
        sort_order: str = "asc",
        **kwargs,
    ) -> tuple[List[Author], int]:
        """
        Get a paginated list of non-deleted authors with optional filtering and sorting.
        """
        query = select(Author).where(Author.deleted == False)
        # name/last_name filters
        if search:
            # search in last_name or name
            query = query.where(
                (Author.last_name.ilike(f"%{search}%"))
                | (Author.name.ilike(f"%{search}%"))
            )
        if start_with:
            query = query.where(Author.last_name.ilike(f"{start_with}%"))
        if ends_with:
            query = query.where(Author.last_name.ilike(f"%{ends_with}"))
        if exact_name:
            query = query.where(Author.name == exact_name)
        if filter_read is not None:
            # Join through association to books; use any() via SQL Alchemy relationships if available
            from librium.database import Book

            query = (
                query.join(Author.books).join(Book).where(Book.read.is_(filter_read))
            )
        total_count = len(Session.scalars(query).unique().all())
        # sorting
        order_attr = Author.last_name
        if sort_order.lower() == "desc":
            query = query.order_by(order_attr.desc())
        else:
            query = query.order_by(order_attr.asc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        authors = Session.scalars(query).unique().all()
        return authors, total_count
