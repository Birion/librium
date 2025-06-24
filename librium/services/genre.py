"""
Genre service for the Librium application.

This module provides a service for interacting with the Genre model.
"""

from typing import List, Optional

from librium.database import Genre, Session, transactional, read_only


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
