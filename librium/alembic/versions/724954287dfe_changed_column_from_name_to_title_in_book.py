"""Changed column from `name` to `title` in Book

Revision ID: 724954287dfe
Revises: 1fcb66c3b155
Create Date: 2018-06-25 13:07:11.820825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '724954287dfe'
down_revision = '1fcb66c3b155'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("book", "name", new_column_name="title")


def downgrade():
    op.alter_column("book", "title", new_column_name="name")
