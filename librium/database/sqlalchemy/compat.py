"""
Compatibility layer for transitioning from Pony ORM to SQLAlchemy.

This module provides compatibility functions and classes to make the transition
from Pony ORM to SQLAlchemy smoother. It allows existing code to continue
working with minimal changes while gradually migrating to SQLAlchemy.
"""

from functools import wraps
from typing import Callable, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session as SQLAlchemySession

from librium.database.sqlalchemy.db import (
    Author,
    AuthorOrdering,
    Book,
    Format,
    Genre,
    Language,
    Publisher,
    Series,
    SeriesIndex,
    Session,
)

# Type variable for generic functions
T = TypeVar("T")

# Map Pony ORM entity names to SQLAlchemy models
entity_map = {
    "Book": Book,
    "Author": Author,
    "Publisher": Publisher,
    "Format": Format,
    "Language": Language,
    "Genre": Genre,
    "Series": Series,
    "SeriesIndex": SeriesIndex,
    "AuthorOrdering": AuthorOrdering,
}


class ObjectNotFound(Exception):
    """Exception raised when an object is not found in the database."""

    pass


class PonyCompatSession:
    """
    A compatibility wrapper around SQLAlchemy's Session class.

    This class provides methods that mimic Pony ORM's API to make the transition
    smoother.
    """

    def __init__(self, session: SQLAlchemySession):
        """
        Initialize a new compatibility session.

        Args:
            session: The SQLAlchemy session to wrap
        """
        self.session = session

    def get(self, entity: Type[T], **kwargs) -> Optional[T]:
        """
        Get an entity by its attributes.

        Args:
            entity: The entity class
            **kwargs: The attributes to filter by

        Returns:
            The entity if found, None otherwise
        """
        return self.session.query(entity).filter_by(**kwargs).first()

    def select(self, entity: Type[T]) -> List[T]:
        """
        Select all entities of a given type.

        Args:
            entity: The entity class

        Returns:
            A list of all entities of the given type
        """
        return self.session.query(entity).all()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self.session.rollback()

    def flush(self) -> None:
        """Flush the current transaction."""
        self.session.flush()

    def close(self) -> None:
        """Close the session."""
        self.session.close()


def db_session(func: Callable) -> Callable:
    """
    Decorator that wraps a function in a database session.

    This decorator is compatible with Pony ORM's db_session decorator.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            # Make the session available to the function
            kwargs["_session"] = PonyCompatSession(session)
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    return wrapper


def select(query_lambda):
    """
    Compatibility function for Pony ORM's select function.

    This function converts a Pony ORM-style query lambda to an SQLAlchemy query.

    Args:
        query_lambda: A lambda function that defines the query

    Returns:
        A list of entities that match the query
    """
    # This is a simplified implementation that doesn't handle all Pony ORM query features.
    # For complex queries, you'll need to rewrite them using SQLAlchemy's API.
    session = Session()
    try:
        # Extract the entity type from the lambda function
        entity_type = None
        for entity_name, entity_class in entity_map.items():
            if entity_name.lower() in str(query_lambda):
                entity_type = entity_class
                break

        if entity_type is None:
            raise ValueError("Could not determine entity type from query lambda")

        # For now, just return all entities of the given type
        # In a real implementation, you would parse the lambda and convert it to an SQLAlchemy query
        return session.query(entity_type).all()
    finally:
        session.close()


def commit():
    """Compatibility function for Pony ORM's commit function."""
    session = Session()
    try:
        session.commit()
    finally:
        session.close()


def rollback():
    """Compatibility function for Pony ORM's rollback function."""
    session = Session()
    try:
        session.rollback()
    finally:
        session.close()


def flush():
    """Compatibility function for Pony ORM's flush function."""
    session = Session()
    try:
        session.flush()
    finally:
        session.close()


# Compatibility for Pony ORM's entity[id] syntax
def get_entity_by_id(entity_type: Type[T], entity_id: int) -> T:
    """
    Get an entity by its ID.

    Args:
        entity_type: The entity class
        entity_id: The entity ID

    Returns:
        The entity if found

    Raises:
        ObjectNotFound: If the entity is not found
    """
    session = Session()
    try:
        entity = session.get(entity_type, entity_id)
        if entity is None:
            raise ObjectNotFound(
                f"{entity_type.__name__} with ID {entity_id} not found"
            )
        return entity
    finally:
        session.close()


# Monkeypatch the entity classes to support the entity[id] syntax
for entity_class in entity_map.values():
    entity_class.__class_getitem__ = classmethod(
        lambda cls, key: get_entity_by_id(cls, key)
    )
