"""Added many-to-many languages to books

Revision ID: 30b0ffafc5a8
Revises: 724954287dfe
Create Date: 2018-06-25 15:56:35.812736

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '30b0ffafc5a8'
down_revision = '724954287dfe'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('book_languages',
                    sa.Column('book_id', sa.Integer(), nullable=False),
                    sa.Column('language_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['book_id'], ['book._id'], name=op.f('fk_book_languages_book_id_book')),
                    sa.ForeignKeyConstraint(['language_id'], ['language._id'],
                                            name=op.f('fk_book_languages_language_id_language')),
                    sa.PrimaryKeyConstraint('book_id', 'language_id', name=op.f('pk_book_languages'))
                    )
    op.drop_constraint('fk_book_language_id_language', 'book', type_='foreignkey')
    op.drop_column('book', 'language_id')


def downgrade():
    op.add_column('book', sa.Column('language_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_book_language_id_language', 'book', 'language', ['language_id'], ['_id'])
    op.drop_table('book_languages')
