"""Rename id columns

Revision ID: 1fcb66c3b155
Revises: 5b90c33340d5
Create Date: 2018-06-25 11:45:38.368670

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1fcb66c3b155"
down_revision = "5b90c33340d5"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("author", "id", new_column_name="_id")
    op.alter_column("author", "uuid", new_column_name="_uuid")
    op.alter_column("book", "id", new_column_name="_id")
    op.alter_column("book", "uuid", new_column_name="_uuid")

    op.alter_column("format", "id", new_column_name="_id")
    op.alter_column("genre", "id", new_column_name="_id")
    op.alter_column("language", "id", new_column_name="_id")
    op.alter_column("publisher", "id", new_column_name="_id")
    op.alter_column("series", "id", new_column_name="_id")

    op.create_unique_constraint(op.f("uq_author__uuid"), "author", ["_uuid"])
    op.drop_constraint("uq_author_uuid", "author", type_="unique")
    op.create_unique_constraint(op.f("uq_book__uuid"), "book", ["_uuid"])
    op.drop_constraint("uq_book_uuid", "book", type_="unique")
    op.drop_constraint("fk_book_language_id_language", "book", type_="foreignkey")
    op.drop_constraint("fk_book_format_id_format", "book", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_book_format_id_format"), "book", "format", ["format_id"], ["_id"]
    )
    op.create_foreign_key(
        op.f("fk_book_language_id_language"),
        "book",
        "language",
        ["language_id"],
        ["_id"],
    )
    op.drop_constraint(
        "fk_book_authors_book_id_book", "book_authors", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_book_authors_author_id_author", "book_authors", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_book_authors_author_id_author"),
        "book_authors",
        "author",
        ["author_id"],
        ["_id"],
    )
    op.create_foreign_key(
        op.f("fk_book_authors_book_id_book"),
        "book_authors",
        "book",
        ["book_id"],
        ["_id"],
    )
    op.drop_constraint(
        "fk_book_genres_genre_id_genre", "book_genres", type_="foreignkey"
    )
    op.drop_constraint("fk_book_genres_book_id_book", "book_genres", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_book_genres_genre_id_genre"),
        "book_genres",
        "genre",
        ["genre_id"],
        ["_id"],
    )
    op.create_foreign_key(
        op.f("fk_book_genres_book_id_book"), "book_genres", "book", ["book_id"], ["_id"]
    )
    op.drop_constraint(
        "fk_book_publishers_publisher_id_publisher",
        "book_publishers",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_book_publishers_book_id_book", "book_publishers", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_book_publishers_publisher_id_publisher"),
        "book_publishers",
        "publisher",
        ["publisher_id"],
        ["_id"],
    )
    op.create_foreign_key(
        op.f("fk_book_publishers_book_id_book"),
        "book_publishers",
        "book",
        ["book_id"],
        ["_id"],
    )
    op.drop_constraint(
        "fk_series_index_book_id_book", "series_index", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_series_index_series_id_series", "series_index", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_series_index_series_id_series"),
        "series_index",
        "series",
        ["series_id"],
        ["_id"],
    )
    op.create_foreign_key(
        op.f("fk_series_index_book_id_book"),
        "series_index",
        "book",
        ["book_id"],
        ["_id"],
    )


def downgrade():
    op.alter_column("author", "_id", new_column_name="id")
    op.alter_column("author", "_uuid", new_column_name="uuid")
    op.alter_column("book", "_id", new_column_name="id")
    op.alter_column("book", "_uuid", new_column_name="uuid")

    op.alter_column("format", "_id", new_column_name="id")
    op.alter_column("genre", "_id", new_column_name="id")
    op.alter_column("language", "_id", new_column_name="id")
    op.alter_column("publisher", "_id", new_column_name="id")
    op.alter_column("series", "_id", new_column_name="id")

    op.drop_constraint(
        op.f("fk_series_index_book_id_book"), "series_index", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_series_index_series_id_series"), "series_index", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_series_index_series_id_series",
        "series_index",
        "series",
        ["series_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_series_index_book_id_book", "series_index", "book", ["book_id"], ["id"]
    )
    op.drop_constraint(
        op.f("fk_book_publishers_book_id_book"), "book_publishers", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_book_publishers_publisher_id_publisher"),
        "book_publishers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_book_publishers_book_id_book",
        "book_publishers",
        "book",
        ["book_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_book_publishers_publisher_id_publisher",
        "book_publishers",
        "publisher",
        ["publisher_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_book_genres_book_id_book"), "book_genres", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_book_genres_genre_id_genre"), "book_genres", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_book_genres_book_id_book", "book_genres", "book", ["book_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_book_genres_genre_id_genre", "book_genres", "genre", ["genre_id"], ["id"]
    )
    op.drop_constraint(
        op.f("fk_book_authors_book_id_book"), "book_authors", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_book_authors_author_id_author"), "book_authors", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_book_authors_author_id_author",
        "book_authors",
        "author",
        ["author_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_book_authors_book_id_book", "book_authors", "book", ["book_id"], ["id"]
    )
    op.add_column(
        "book",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('book_id_seq'::regclass)"),
            nullable=False,
        ),
    )
    op.add_column(
        "book", sa.Column("uuid", postgresql.UUID(), autoincrement=False, nullable=True)
    )
    op.drop_constraint(op.f("fk_book_language_id_language"), "book", type_="foreignkey")
    op.drop_constraint(op.f("fk_book_format_id_format"), "book", type_="foreignkey")
    op.create_foreign_key(
        "fk_book_format_id_format", "book", "format", ["format_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_book_language_id_language", "book", "language", ["language_id"], ["id"]
    )
    op.create_unique_constraint("uq_book_uuid", "book", ["uuid"])
    op.drop_constraint(op.f("uq_book__uuid"), "book", type_="unique")
    op.create_unique_constraint("uq_author_uuid", "author", ["uuid"])
    op.drop_constraint(op.f("uq_author__uuid"), "author", type_="unique")
