"""
Authentication service for the Librium application.

This module provides a service for interacting with the Authentication model.
"""

from typing import List, Optional

from sqlalchemy import select

from librium.database import Authentication, Session, read_only, transactional


class AuthenticationService:
    """Service for interacting with the Authentication model."""

    @staticmethod
    @read_only
    def get_by_id(auth_id: int) -> Optional[Authentication]:
        """
        Retrieve an authentication record by its ID.

        Args:
            auth_id (int): The ID of the authentication record.

        Returns:
            Optional[Authentication]: The authentication record if found, otherwise None.
        """
        return Session.get(Authentication, auth_id)

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Authentication]:
        """
        Retrieve an authentication record by username.

        Args:
            name (str): The username to search for.

        Returns:
            Optional[Authentication]: The authentication record if found, otherwise None.
        """
        return Session.scalar(
            select(Authentication).where(Authentication.username == name)
        )

    @staticmethod
    @read_only
    def get_all() -> List[Authentication]:
        """
        Retrieve all authentication records.

        Returns:
            List[Authentication]: A list of all authentication records.
        """
        return Session.scalar(
            select(Authentication).where(Authentication.deleted.is_(False))
        )

    @staticmethod
    @transactional
    def create(
        username: str,
        password: str,
    ) -> Authentication:
        """
        Create a new authentication record.

        Args:
            username (str): The username for the new authentication record.
            password (str): The password for the new authentication record.

        Returns:
            Authentication: The newly created authentication record.
        """
        authentication = Authentication(username=username)
        authentication.set_password(password)
        Session.add(authentication)
        return authentication

    @staticmethod
    @transactional
    def update(auth_id: int, **kwargs) -> Optional[Authentication]:
        """
        Update an existing authentication record.

        Args:
            auth_id (int): The ID of the authentication record to update.
            **kwargs: Fields to update (e.g., password, username).

        Returns:
            Optional[Authentication]: The updated authentication record if found, otherwise None.
        """
        authentication = Session.get(Authentication, auth_id)
        if not authentication:
            return None

        for key, value in kwargs.items():
            if key == "password":
                authentication.set_password(value)
            else:
                setattr(authentication, key, value)

        return authentication

    @staticmethod
    @transactional
    def delete(auth_id: int) -> bool:
        """
        Soft-delete an authentication record by setting its deleted flag.

        Args:
            auth_id (int): The ID of the authentication record to delete.

        Returns:
            bool: True if the record was found and marked as deleted, False otherwise.
        """
        authentication = Session.get(Authentication, auth_id)
        if not authentication:
            return False
        authentication.deleted = True
        return True
