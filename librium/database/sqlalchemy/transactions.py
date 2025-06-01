"""
Transaction management for SQLAlchemy.

This module provides decorators and context managers for managing transactions
in the application. It ensures that database operations are properly wrapped
in transactions to maintain data consistency.
"""

from contextlib import contextmanager
from functools import wraps

from librium.database.sqlalchemy.db import Session


def transactional(func):
    """
    Decorator that wraps a function in a database session.

    This decorator ensures that the function is executed within a database
    session and that changes are committed or rolled back appropriately.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    return wrapper


def read_only(func):
    """
    Decorator that wraps a function in a read-only database session.

    This decorator ensures that the function is executed within a database
    session but does not commit any changes. This is useful for functions
    that only read from the database.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            raise e

    return wrapper


@contextmanager
def transaction_context(read_only=False):
    """
    Context manager for database transactions.

    This context manager ensures that database operations are executed within
    a transaction and that changes are committed or rolled back appropriately.

    Args:
        read_only: Whether the transaction is read-only

    Yields:
        The database session
    """
    session = Session()
    try:
        yield session
        if not read_only:
            session.commit()
    except Exception as e:
        session.rollback()
        raise e


class TransactionContext:
    """
    Context manager for database transactions.

    This context manager ensures that database operations are executed within
    a transaction and that changes are committed or rolled back appropriately.
    """

    def __init__(self, read_only=False):
        """
        Initialize a new transaction context.

        Args:
            read_only: Whether the transaction is read-only
        """
        self.read_only = read_only
        self.session = None

    def __enter__(self):
        """
        Enter the transaction context.

        Returns:
            The database session
        """
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.

        If an exception occurred, roll back the transaction. Otherwise, commit
        the transaction if it's not read-only.

        Args:
            exc_type: The exception type, if an exception occurred
            exc_val: The exception value, if an exception occurred
            exc_tb: The exception traceback, if an exception occurred

        Returns:
            True if the exception was handled, False otherwise
        """
        if exc_type is not None:
            self.session.rollback()
            return False

        if not self.read_only:
            self.session.commit()

        return True
