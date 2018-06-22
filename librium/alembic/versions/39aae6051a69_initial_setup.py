"""Initial setup

Revision ID: 39aae6051a69
Revises: 
Create Date: 2018-06-22 16:23:11.848935

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils as sau


# revision identifiers, used by Alembic.
revision = '39aae6051a69'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('middle_name', sa.String(length=50), nullable=True),
    sa.Column('prefix', sa.String(length=20), nullable=True),
    sa.Column('suffix', sa.String(length=20), nullable=True),
    sa.Column('uuid', sau.UUIDType(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_author')),
    sa.UniqueConstraint('uuid', name=op.f('uq_author_uuid'))
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('page_count', sa.Integer(), nullable=True),
    sa.Column('isbn', sa.String(length=13), nullable=True),
    sa.Column('read', sa.Boolean(), nullable=False),
    sa.Column('uuid', sau.UUIDType(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_book')),
    sa.UniqueConstraint('isbn', name=op.f('uq_book_isbn')),
    sa.UniqueConstraint('uuid', name=op.f('uq_book_uuid'))
    )
    op.create_table('format',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_format'))
    )
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_genre'))
    )
    op.create_table('language',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_language'))
    )
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publisher'))
    )
    op.create_table('series',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_series'))
    )
    op.create_table('book_authors',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], name=op.f('fk_book_authors_author_id_author')),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], name=op.f('fk_book_authors_book_id_book')),
    sa.PrimaryKeyConstraint('book_id', 'author_id', name=op.f('pk_book_authors'))
    )
    op.create_table('book_genres',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], name=op.f('fk_book_genres_book_id_book')),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], name=op.f('fk_book_genres_genre_id_genre')),
    sa.PrimaryKeyConstraint('book_id', 'genre_id', name=op.f('pk_book_genres'))
    )
    op.create_table('book_publishers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('publisher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], name=op.f('fk_book_publishers_book_id_book')),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], name=op.f('fk_book_publishers_publisher_id_publisher')),
    sa.PrimaryKeyConstraint('book_id', 'publisher_id', name=op.f('pk_book_publishers'))
    )
    op.create_table('series_index',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('series_id', sa.Integer(), nullable=False),
    sa.Column('idx', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], name=op.f('fk_series_index_book_id_book')),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], name=op.f('fk_series_index_series_id_series')),
    sa.PrimaryKeyConstraint('book_id', 'series_id', name=op.f('pk_series_index'))
    )


def downgrade():
    op.drop_table('series_index')
    op.drop_table('book_publishers')
    op.drop_table('book_genres')
    op.drop_table('book_authors')
    op.drop_table('series')
    op.drop_table('publisher')
    op.drop_table('language')
    op.drop_table('genre')
    op.drop_table('format')
    op.drop_table('book')
    op.drop_table('author')
