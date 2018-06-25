"""init

Revision ID: e7dcf3a3833e
Revises: d779b6fa5161
Create Date: 2018-06-25 18:14:00.628593

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils as sau


# revision identifiers, used by Alembic.
revision = "e7dcf3a3833e"
down_revision = "d779b6fa5161"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "author",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("middle_name", sa.String(length=50), nullable=True),
        sa.Column("prefix", sa.String(length=20), nullable=True),
        sa.Column("suffix", sa.String(length=20), nullable=True),
        sa.Column("_uuid", sau.UUIDType(), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_author")),
        sa.UniqueConstraint("_uuid", name=op.f("uq_author__uuid")),
    )
    op.create_table(
        "format",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_format")),
    )
    op.create_table(
        "genre",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_genre")),
    )
    op.create_table(
        "language",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_language")),
    )
    op.create_table(
        "publisher",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_publisher")),
    )
    op.create_table(
        "series",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_series")),
        sa.UniqueConstraint("name", name=op.f("uq_series_name")),
    )
    op.create_table(
        "book",
        sa.Column("_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("isbn", sa.String(length=13), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("_uuid", sau.UUIDType(), nullable=True),
        sa.Column("format_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["format_id"], ["format._id"], name=op.f("fk_book_format_id_format")
        ),
        sa.PrimaryKeyConstraint("_id", name=op.f("pk_book")),
        sa.UniqueConstraint("_uuid", name=op.f("uq_book__uuid")),
    )
    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["author._id"], name=op.f("fk_book_authors_author_id_author")
        ),
        sa.ForeignKeyConstraint(
            ["book_id"], ["book._id"], name=op.f("fk_book_authors_book_id_book")
        ),
        sa.PrimaryKeyConstraint("book_id", "author_id", name=op.f("pk_book_authors")),
    )
    op.create_table(
        "book_genres",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["book._id"], name=op.f("fk_book_genres_book_id_book")
        ),
        sa.ForeignKeyConstraint(
            ["genre_id"], ["genre._id"], name=op.f("fk_book_genres_genre_id_genre")
        ),
        sa.PrimaryKeyConstraint("book_id", "genre_id", name=op.f("pk_book_genres")),
    )
    op.create_table(
        "book_languages",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["book._id"], name=op.f("fk_book_languages_book_id_book")
        ),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language._id"],
            name=op.f("fk_book_languages_language_id_language"),
        ),
        sa.PrimaryKeyConstraint(
            "book_id", "language_id", name=op.f("pk_book_languages")
        ),
    )
    op.create_table(
        "book_publishers",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("publisher_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["book._id"], name=op.f("fk_book_publishers_book_id_book")
        ),
        sa.ForeignKeyConstraint(
            ["publisher_id"],
            ["publisher._id"],
            name=op.f("fk_book_publishers_publisher_id_publisher"),
        ),
        sa.PrimaryKeyConstraint(
            "book_id", "publisher_id", name=op.f("pk_book_publishers")
        ),
    )
    op.create_table(
        "series_index",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.Column("idx", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["book._id"], name=op.f("fk_series_index_book_id_book")
        ),
        sa.ForeignKeyConstraint(
            ["series_id"], ["series._id"], name=op.f("fk_series_index_series_id_series")
        ),
        sa.PrimaryKeyConstraint(
            "book_id", "series_id", "idx", name=op.f("pk_series_index")
        ),
    )


def downgrade():
    op.drop_table("series_index")
    op.drop_table("book_publishers")
    op.drop_table("book_languages")
    op.drop_table("book_genres")
    op.drop_table("book_authors")
    op.drop_table("book")
    op.drop_table("series")
    op.drop_table("publisher")
    op.drop_table("language")
    op.drop_table("genre")
    op.drop_table("format")
    op.drop_table("author")
