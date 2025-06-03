"""Add indexes for frequently queried fields

Revision ID: add_indexes
Revises: initial
Create Date: 2025-05-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_indexes"
down_revision = "initial"
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes for Book table
    op.create_index("idx_book_isbn", "book", ["isbn"], unique=False)
    op.create_index("idx_book_read", "book", ["read"], unique=False)
    op.create_index("idx_book_released", "book", ["released"], unique=False)
    op.create_index("idx_book_created_at", "book", ["created_at"], unique=False)

    # Add indexes for Author table
    op.create_index("idx_author_first_name", "author", ["first_name"], unique=False)
    op.create_index("idx_author_last_name", "author", ["last_name"], unique=False)

    # Add indexes for Publisher table
    op.create_index("idx_publisher_name", "publisher", ["name"], unique=False)

    # Add indexes for Format table
    op.create_index("idx_format_name", "format", ["name"], unique=False)

    # Add indexes for Language table
    op.create_index("idx_language_name", "language", ["name"], unique=False)

    # Add indexes for Genre table
    op.create_index("idx_genre_name", "genre", ["name"], unique=False)

    # Add indexes for Series table
    op.create_index(
        "idx_series_name", "series", ["name"], unique=True
    )  # Already has a unique constraint


def downgrade():
    # Remove indexes for Book table
    op.drop_index("idx_book_title", table_name="book")
    op.drop_index("idx_book_isbn", table_name="book")
    op.drop_index("idx_book_read", table_name="book")
    op.drop_index("idx_book_released", table_name="book")
    op.drop_index("idx_book_created_at", table_name="book")

    # Remove indexes for Author table
    op.drop_index("idx_author_first_name", table_name="author")
    op.drop_index("idx_author_last_name", table_name="author")
    op.drop_index("idx_author_name", table_name="author")

    # Remove indexes for Publisher table
    op.drop_index("idx_publisher_name", table_name="publisher")

    # Remove indexes for Format table
    op.drop_index("idx_format_name", table_name="format")

    # Remove indexes for Language table
    op.drop_index("idx_language_name", table_name="language")

    # Remove indexes for Genre table
    op.drop_index("idx_genre_name", table_name="genre")

    # Remove indexes for Series table
    op.drop_index("idx_series_name", table_name="series")
