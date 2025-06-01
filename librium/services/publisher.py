"""
Publisher service for the Librium application.

This module provides a service for interacting with the Publisher model.
"""

from typing import List, Optional

from librium.database import Publisher, Session, transactional, read_only


class PublisherService:
    """Service for interacting with the Publisher model."""

    @staticmethod
    @read_only
    def get_by_id(publisher_id: int) -> Optional[Publisher]:
        """
        Get a publisher by its ID.

        Args:
            publisher_id: The ID of the publisher

        Returns:
            The publisher if found, None otherwise
        """
        return Session.get(Publisher, publisher_id)

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Publisher]:
        """
        Get a publisher by its name.

        Args:
            name: The name of the publisher

        Returns:
            The publisher if found, None otherwise
        """
        return Session.get(Publisher, {"name": name})

    @staticmethod
    @read_only
    def get_all() -> List[Publisher]:
        """
        Get all publishers.

        Returns:
            A list of all publishers
        """
        return list(Session.query(Publisher).order_by(Publisher.name))

    @staticmethod
    @transactional
    def create(name: str) -> Publisher:
        """
        Create a new publisher.

        Args:
            name: The name of the publisher

        Returns:
            The created publisher
        """
        if not name or not name.strip():
            raise ValueError("Publisher name cannot be empty")

        if len(name) > 50:
            raise ValueError("Publisher name cannot be longer than 50 characters")

        publisher = Publisher(name=name)
        Session.add(publisher)
        return publisher

    @staticmethod
    @transactional
    def update(publisher_id: int, name: str) -> Optional[Publisher]:
        """
        Update a publisher.

        Args:
            publisher_id: The ID of the publisher to update
            name: The new name of the publisher

        Returns:
            The updated publisher if found, None otherwise
        """
        publisher = Session.get(Publisher, publisher_id)
        if not publisher:
            return None

        if not name or not name.strip():
            raise ValueError("Publisher name cannot be empty")

        if len(name) > 50:
            raise ValueError("Publisher name cannot be longer than 50 characters")

        publisher.name = name
        return publisher

    @staticmethod
    @transactional
    def delete(publisher_id: int) -> bool:
        """
        Delete a publisher.

        Args:
            publisher_id: The ID of the publisher to delete

        Returns:
            True if the publisher was deleted, False otherwise
        """
        publisher = Session.get(Publisher, publisher_id)
        if not publisher:
            return False

        publisher.delete()
        return True
