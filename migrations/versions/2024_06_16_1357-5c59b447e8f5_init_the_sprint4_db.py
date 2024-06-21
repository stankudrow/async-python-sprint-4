"""init the sprint4 database

Revision ID: 5c59b447e8f5
Revises: 
Create Date: 2024-06-16 13:57:49.196181
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c59b447e8f5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# tables
URIS_TABLE: str = "uris"

# columns
SHORT_URI_COL = "shorten_uri"

# indexes
IDX_SUFFIX = "idx"
SHORT_URI_INDEX = f"{SHORT_URI_COL}_{IDX_SUFFIX}"


def upgrade() -> None:
    op.create_table(
        URIS_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uri", sa.Text(), nullable=False),
        sa.Column(SHORT_URI_COL, sa.String, unique=True, nullable=False),
    )
    op.create_index(
        index_name=SHORT_URI_INDEX, table_name=URIS_TABLE, columns=[SHORT_URI_COL]
    )


def downgrade() -> None:
    op.drop_index(
        index_name=SHORT_URI_INDEX,
        table_name=URIS_TABLE,
        if_exists=True,
    )
    op.drop_table(URIS_TABLE)
