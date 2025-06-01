"""
Language service for the Librium application.

This module provides a service for interacting with the Language model.
"""

from typing import List, Optional

from librium.database import Language, Session, transactional, read_only


class LanguageService:
    """Service for interacting with the Language model."""

    @staticmethod
    @read_only
    def get_by_id(language_id: int) -> Optional[Language]:
        """
        Get a language by its ID.

        Args:
            language_id: The ID of the language

        Returns:
            The language if found, None otherwise
        """
        return Session.get(Language, language_id)

    @staticmethod
    @read_only
    def get_by_name(name: str) -> Optional[Language]:
        """
        Get a language by its name.

        Args:
            name: The name of the language

        Returns:
            The language if found, None otherwise
        """
        return Session.get(Language, {"name": name})

    @staticmethod
    @read_only
    def get_all() -> List[Language]:
        """
        Get all languages.

        Returns:
            A list of all languages
        """
        return list(Session.query(Language).order_by(Language.name))

    @staticmethod
    @transactional
    def create(name: str) -> Language:
        """
        Create a new language.

        Args:
            name: The name of the language

        Returns:
            The created language
        """
        if not name or not name.strip():
            raise ValueError("Language name cannot be empty")

        if len(name) > 50:
            raise ValueError("Language name cannot be longer than 50 characters")

        language_obj = Language(name=name)
        Session.add(language_obj)
        return language_obj

    @staticmethod
    @transactional
    def update(language_id: int, name: str) -> Optional[Language]:
        """
        Update a language.

        Args:
            language_id: The ID of the language to update
            name: The new name of the language

        Returns:
            The updated language if found, None otherwise
        """
        language_obj = Session.get(Language, language_id)
        if not language_obj:
            return None

        if not name or not name.strip():
            raise ValueError("Language name cannot be empty")

        if len(name) > 50:
            raise ValueError("Language name cannot be longer than 50 characters")

        language_obj.name = name
        return language_obj

    @staticmethod
    @transactional
    def delete(language_id: int) -> bool:
        """
        Delete a language.

        Args:
            language_id: The ID of the language to delete

        Returns:
            True if the language was deleted, False otherwise
        """
        language_obj = Session.get(Language, language_id)
        if not language_obj:
            return False

        language_obj.delete()
        return True
