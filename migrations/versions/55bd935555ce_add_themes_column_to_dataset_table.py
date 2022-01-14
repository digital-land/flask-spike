"""add themes column to dataset table

Revision ID: 55bd935555ce
Revises: c931b5cb720a
Create Date: 2022-01-06 16:43:51.466677

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "55bd935555ce"
down_revision = "c931b5cb720a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "dataset", sa.Column("themes", postgresql.ARRAY(sa.Text()), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("dataset", "themes")
    # ### end Alembic commands ###