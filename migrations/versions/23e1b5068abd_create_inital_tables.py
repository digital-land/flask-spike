"""create inital tables

Revision ID: 23e1b5068abd
Revises:
Create Date: 2021-12-21 19:18:47.986355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = "23e1b5068abd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        "entity",
        sa.Column("entity", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("dataset", sa.Text(), nullable=True),
        sa.Column("json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("organisation_entity", sa.Integer(), nullable=True),
        sa.Column("prefix", sa.Text(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=True),
        sa.Column("typology", sa.Text(), nullable=True),
        sa.Column("geojson", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="MULTIPOLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column(
            "point",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("entity"),
    )
    op.create_index(
        "idx_entity_columns",
        "entity",
        ["entity", "name", "entry_date", "start_date"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_entity_columns", table_name="entity")
    op.drop_index("idx_entity_geometry", table_name="entity")
    op.drop_index("idx_entity_point", table_name="entity")
    op.drop_table("entity")
    op.execute("DROP EXTENSION IF EXISTS postgis")
    # ### end Alembic commands ###