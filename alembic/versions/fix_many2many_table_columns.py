"""empty message

Revision ID: fix_many2many_table_columns
Revises: add_indexes
Create Date: 2025-05-29 15:27:47.507594

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fix_many2many_table_columns"
down_revision = "add_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("book_publishers", "book", new_column_name="book_id")
    op.alter_column("book_publishers", "publisher", new_column_name="publisher_id")
    op.alter_column("book_languages", "book", new_column_name="book_id")
    op.alter_column("book_languages", "language", new_column_name="language_id")
    op.alter_column("book_genres", "book", new_column_name="book_id")
    op.alter_column("book_genres", "genre", new_column_name="genre_id")
    op.alter_column("book_authors", "book", new_column_name="book_id")
    op.alter_column("book_authors", "author", new_column_name="author_id")
    op.alter_column("series_index", "book", new_column_name="book_id")
    op.alter_column("series_index", "series", new_column_name="series_id")


def downgrade():
    op.alter_column("book_publishers", "book_id", new_column_name="book")
    op.alter_column("book_publishers", "publisher_id", new_column_name="publisher")
    op.alter_column("book_languages", "book_id", new_column_name="book")
    op.alter_column("book_languages", "language_id", new_column_name="language")
    op.alter_column("book_genres", "book_id", new_column_name="book")
    op.alter_column("book_genres", "genre_id", new_column_name="genre")
    op.alter_column("book_authors", "book_id", new_column_name="book")
    op.alter_column("book_authors", "author_id", new_column_name="author")
    op.alter_column("series_index", "book_id", new_column_name="book")
    op.alter_column("series_index", "series_id", new_column_name="series")
