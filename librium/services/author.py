"""
Author service for the Librium application.

This module provides a service for interacting with the Author model.
"""

from typing import List, Optional

from sqlalchemy import select

from librium.database import Author, Session, read_only, transactional


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
        selector = (
            select(Author)
            .where(Author.first_name == first_name)
            .where(Author.last_name == last_name)
            .where(Author.middle_name == middle_name)
            .where(Author.prefix == prefix)
            .where(Author.suffix == suffix)
            .where(Author.deleted == False)
        )

        return Session.scalar(selector).unique().one_or_none()

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
        **kwargs
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
