"""
Database backup and restore functionality.

This module provides functions for backing up the database and restoring it from a backup.
"""

import os
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from librium.database.sqlalchemy.db import engine


def get_backup_directory() -> Path:
    """
    Get the directory where backups are stored.

    Returns:
        The backup directory path
    """
    backup_dir = Path.cwd() / "backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def create_backup(filename: Optional[str] = None) -> Path:
    """
    Create a backup of the database.

    Args:
        filename: The name of the backup file (without extension)

    Returns:
        The path to the backup file
    """
    # Get the database file path from the engine
    db_file = engine.url.database

    # Generate a filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}"

    # Ensure the filename has a .sqlite extension
    if not filename.endswith(".sqlite"):
        filename += ".sqlite"

    # Get the backup directory
    backup_dir = get_backup_directory()
    backup_file = backup_dir / filename

    # Create a connection to the source database
    source_conn = sqlite3.connect(db_file)

    # Create a connection to the backup database
    backup_conn = sqlite3.connect(str(backup_file))

    # Backup the database
    source_conn.backup(backup_conn)

    # Close the connections
    source_conn.close()
    backup_conn.close()

    return backup_file


def restore_from_backup(backup_file: Path) -> bool:
    """
    Restore the database from a backup.

    Args:
        backup_file: The path to the backup file

    Returns:
        True if the restore was successful, False otherwise
    """
    # Get the database file path from the engine
    db_file = engine.url.database

    # Check if the backup file exists
    if not backup_file.exists():
        return False

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Create a connection to the backup database
        backup_conn = sqlite3.connect(str(backup_file))

        # Create a connection to the temporary database
        temp_conn = sqlite3.connect(temp_path)

        # Backup the backup database to the temporary database
        backup_conn.backup(temp_conn)

        # Close the connections
        backup_conn.close()
        temp_conn.close()

        # Dispose of the engine to close all connections
        engine.dispose()

        # Replace the database file with the temporary file
        shutil.copy2(temp_path, db_file)

        return True
    except Exception as e:
        print(f"Error restoring from backup: {e}")
        return False
    finally:
        # Remove the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def list_backups() -> List[Path]:
    """
    List all available backups.

    Returns:
        A list of paths to backup files
    """
    backup_dir = get_backup_directory()
    return sorted(
        backup_dir.glob("*.sqlite"), key=lambda x: x.stat().st_mtime, reverse=True
    )


def delete_backup(backup_file: Path) -> bool:
    """
    Delete a backup file.

    Args:
        backup_file: The path to the backup file

    Returns:
        True if the backup was deleted, False otherwise
    """
    if not backup_file.exists():
        return False

    try:
        backup_file.unlink()
        return True
    except Exception as e:
        print(f"Error deleting backup: {e}")
        return False
