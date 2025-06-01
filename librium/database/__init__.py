"""
Database models and utilities for the Librium application.

This module re-exports the SQLAlchemy models and compatibility functions with
the same names as the Pony ORM ones, allowing the existing code to continue
working with minimal changes.
"""

# Re-export the SQLAlchemy models and compatibility functions
from librium.database.sqlalchemy.db import (
    Book,
    Author,
    Publisher,
    Format,
    Language,
    Genre,
    Series,
    SeriesIndex,
    AuthorOrdering,
    Session,
    Base,
    engine,
    create_tables,
    drop_tables,
    init_db,
)

# from librium.database.sqlalchemy.compat import (
#     db_session, select, commit, rollback, flush, ObjectNotFound
# )
from librium.database.sqlalchemy.transactions import (
    transactional,
    read_only,
    transaction_context,
    TransactionContext,
)
from librium.database.backup import (
    create_backup,
    restore_from_backup,
    list_backups,
    delete_backup,
    get_backup_directory,
)

# Define __all__ to control what gets imported with "from librium.database import *"
__all__ = [
    # Models
    "Book",
    "Author",
    "Publisher",
    "Format",
    "Language",
    "Genre",
    "Series",
    "SeriesIndex",
    "AuthorOrdering",
    # Session management
    "Session",
    "Base",
    "engine",
    "create_tables",
    "drop_tables",
    "init_db",
    # # Compatibility functions
    # 'db_session', 'select', 'commit', 'rollback', 'flush', 'ObjectNotFound',
    # Transaction management
    "transactional",
    "read_only",
    "transaction_context",
    "TransactionContext",
    # Backup and restore
    "create_backup",
    "restore_from_backup",
    "list_backups",
    "delete_backup",
    "get_backup_directory",
]
