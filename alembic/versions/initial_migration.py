"""Initial migration

Revision ID: initial
Revises:
Create Date: 2025-05-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("book", "format", new_column_name="format_id")

    op.add_column(
        "book",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("book", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "author",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("author", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "publisher",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("publisher", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "format",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("format", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "language",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("language", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "genre",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("genre", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "series",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default="CURRENT_TIMESTAMP",
        ),
    )
    op.add_column("series", sa.Column("updated_at", sa.DateTime(), nullable=True))


def downgrade():
    # Drop tables in reverse order
    op.drop_column("book", "created_at")
    op.drop_column("book", "updated_at")
    op.drop_column("author", "created_at")
    op.drop_column("author", "updated_at")
    op.drop_column("publisher", "created_at")
    op.drop_column("publisher", "updated_at")
    op.drop_column("format", "created_at")
    op.drop_column("format", "updated_at")
    op.drop_column("language", "created_at")
    op.drop_column("language", "updated_at")
    op.drop_column("genre", "created_at")
    op.drop_column("genre", "updated_at")
    op.drop_column("series", "created_at")
    op.drop_column("series", "updated_at")
    op.drop_column("format", "created_at")
    op.drop_column("format", "updated_at")
