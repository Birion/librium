"""
Format service for the Librium application.

This module provides a service for interacting with the Format model.
"""

from typing import List, Optional

from librium.database import Format, Session, transactional, read_only


class FormatService:
    """Service for interacting with the Format model."""

    @staticmethod
    @read_only
    def get_by_id(format_id: int) -> Optional[Format]:
        """
        Get a format by its ID.

        Args:
            format_id: The ID of the format

        Returns:
            The format if found, None otherwise
        """
        return Session.get(Format, format_id)

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Format]:
        """
        Get a format by its name.

        Args:
            name: The name of the format

        Returns:
            The format if found, None otherwise
        """
        return Session.get(Format, {"name": name})

    @staticmethod
    @read_only
    def get_all() -> List[Format]:
        """
        Get all formats.

        Returns:
            A list of all formats
        """
        return list(Session.query(Format).order_by(Format.name))

    @staticmethod
    @transactional
    def create(name: str) -> Format:
        """
        Create a new format.

        Args:
            name: The name of the format

        Returns:
            The created format
        """
        if not name or not name.strip():
            raise ValueError("Format name cannot be empty")

        if len(name) > 50:
            raise ValueError("Format name cannot be longer than 50 characters")

        format_obj = Format(name=name)
        Session.add(format_obj)
        return format_obj

    @staticmethod
    @transactional
    def update(format_id: int, name: str) -> Optional[Format]:
        """
        Update a format.

        Args:
            format_id: The ID of the format to update
            name: The new name of the format

        Returns:
            The updated format if found, None otherwise
        """
        format_obj = Session.get(Format, format_id)
        if not format_obj:
            return None

        if not name or not name.strip():
            raise ValueError("Format name cannot be empty")

        if len(name) > 50:
            raise ValueError("Format name cannot be longer than 50 characters")

        format_obj.name = name
        return format_obj

    @staticmethod
    @transactional
    def delete(format_id: int) -> bool:
        """
        Delete a format.

        Args:
            format_id: The ID of the format to delete

        Returns:
            True if the format was deleted, False otherwise
        """
        format_obj = Session.get(Format, format_id)
        if not format_obj:
            return False

        format_obj.delete()
        return True
