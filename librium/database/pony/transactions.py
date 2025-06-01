"""
Transaction management for Pony ORM.

This module provides decorators and context managers for managing transactions
in the application. It ensures that database operations are properly wrapped
in transactions to maintain data consistency.
"""

from functools import wraps

from pony.orm import db_session, commit, rollback


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
        with db_session:
            try:
                result = func(*args, **kwargs)
                # No need to call commit() explicitly as db_session will do it
                return result
            except Exception as e:
                rollback()
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
        with db_session:
            return func(*args, **kwargs)

    return wrapper


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

    def __enter__(self):
        """
        Enter the transaction context.
        """
        return self

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
            rollback()
            return False

        if not self.read_only:
            commit()

        return True
