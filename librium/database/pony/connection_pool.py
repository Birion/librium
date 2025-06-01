"""
Connection pooling implementation for Pony ORM with SQLite.

This module provides a connection pool for SQLite databases to improve performance
by reusing database connections instead of creating new ones for each request.
"""

import os
import sqlite3
import threading
from queue import Queue, Empty
from typing import Dict, Optional, List

from pony.orm import Database

# Maximum number of connections in the pool
MAX_CONNECTIONS = 10

# Maximum idle time for a connection in seconds
MAX_IDLE_TIME = 300  # 5 minutes

# Lock for thread-safe operations
_lock = threading.RLock()

# Connection pools for different database files
_pools: Dict[str, "ConnectionPool"] = {}


class ConnectionPool:
    """
    A simple connection pool for SQLite connections.
    """

    def __init__(self, db_file: str, max_connections: int = MAX_CONNECTIONS):
        """
        Initialize a new connection pool.

        Args:
            db_file: Path to the SQLite database file
            max_connections: Maximum number of connections to keep in the pool
        """
        self.db_file = db_file
        self.max_connections = max_connections
        self.connections: Queue = Queue(maxsize=max_connections)
        self.active_connections: int = 0
        self.lock = threading.RLock()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection from the pool or create a new one if the pool is empty.

        Returns:
            A SQLite connection
        """
        with self.lock:
            try:
                # Try to get a connection from the pool
                connection = self.connections.get_nowait()
                return connection
            except Empty:
                # If the pool is empty, create a new connection if we haven't reached the limit
                if self.active_connections < self.max_connections:
                    connection = sqlite3.connect(self.db_file, check_same_thread=False)
                    self.active_connections += 1
                    return connection
                else:
                    # If we've reached the limit, wait for a connection to be returned
                    connection = self.connections.get()
                    return connection

    def return_connection(self, connection: sqlite3.Connection) -> None:
        """
        Return a connection to the pool.

        Args:
            connection: The SQLite connection to return
        """
        with self.lock:
            self.connections.put(connection)

    def close_all(self) -> None:
        """
        Close all connections in the pool.
        """
        with self.lock:
            while not self.connections.empty():
                try:
                    connection = self.connections.get_nowait()
                    connection.close()
                except Empty:
                    break
            self.active_connections = 0


def get_connection_pool(db_file: str) -> ConnectionPool:
    """
    Get or create a connection pool for the specified database file.

    Args:
        db_file: Path to the SQLite database file

    Returns:
        A connection pool for the database
    """
    with _lock:
        if db_file not in _pools:
            _pools[db_file] = ConnectionPool(db_file)
        return _pools[db_file]


def setup_connection_pool(db: Database, db_file: str) -> None:
    """
    Set up connection pooling for a Pony ORM database.

    Args:
        db: The Pony ORM database instance
        db_file: Path to the SQLite database file
    """
    # Get or create a connection pool for the database
    pool = get_connection_pool(db_file)

    # Override the _get_connection method to use our connection pool
    original_get_connection = db._get_connection

    def _get_pooled_connection(*args, **kwargs):
        # For in-memory databases, use the original method
        if db_file == ":memory:":
            return original_get_connection(*args, **kwargs)

        # For file-based databases, use the connection pool
        connection = pool.get_connection()
        return connection

    # Override the _release_connection method to return connections to the pool
    original_release_connection = db._release_connection

    def _release_pooled_connection(connection, *args, **kwargs):
        # For in-memory databases, use the original method
        if db_file == ":memory:":
            return original_release_connection(connection, *args, **kwargs)

        # For file-based databases, return the connection to the pool
        pool.return_connection(connection)

    # Apply the overrides
    db._get_connection = _get_pooled_connection
    db._release_connection = _release_pooled_connection


def close_all_pools() -> None:
    """
    Close all connection pools.
    """
    with _lock:
        for pool in _pools.values():
            pool.close_all()
        _pools.clear()
